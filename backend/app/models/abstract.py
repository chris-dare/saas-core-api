"""The :mod:`app.models.abstract` module contains abstract classes for building persistent models
data concerning organizations on HyperSenta
"""
# Author: Christopher Dare

import uuid as uuid_pkg
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

import pycountry
import sqlalchemy as sa
from app.schemas import (
    OperatingCountryType,
    PaymentContributionType,
    WalletCurrencyType,
)
from app.utils import quantize_monetary_number
from pydantic import validator
from sqlmodel import AutoString, Column, DateTime, Field, SQLModel


class TimeStampedModel(SQLModel):
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        unique=True,
        index=True,
        nullable=False,
        description="External UUID",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow),
        description="Date and time the object was created",
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=datetime.utcnow, default=datetime.utcnow
        ),
        description="Last date and time the object was updated",
    )


class AbstractHealthcareWalletPolicy(SQLModel, table=False):
    coinsurance: Optional[Decimal] = Field(
        description="The percentage of covered medical expenses a user pays"
        + " after they've met their deductible",
        nullable=True,
        default=quantize_monetary_number(0),
        sa_column=sa.Column(
            name="coinsurance",
            type_=sa.DECIMAL(precision=3, scale=2),
            nullable=False,
            comment="The percentage of covered medical expenses a user pays"
            + " after they've met their deductible."
            + " On a scale of 0 to 1, where 1 is 100%",
        ),
    )
    contribution_type: Optional[PaymentContributionType] = Field(
        description="Type of contribution (copay of coinsurance). "
        + "Defaults to coinsurance",
        default=PaymentContributionType.COINSURANCE,
        sa_column=Column(
            name="contribution_type",
            type_=sa.String(15),
            nullable=True,
            index=True,
            comment="Type of contribution (copay of coinsurance). "
            + "Defaults to coinsurance",
        ),
    )
    copay_amount: Optional[Decimal] = Field(
        description="The set amount a user pays to their medical provider"
        + " when they receive services."
        + " These are overidden by service specific copay amounts",
        nullable=True,
        default=quantize_monetary_number(0),
        sa_column=sa.Column(
            name="copay_amount",
            type_=sa.DECIMAL(precision=18, scale=2),
            nullable=False,
            comment="The set amount a user pays to their medical provider"
            + " when they receive services."
            + " These are overidden by service specific copay amounts",
        ),
    )
    currency: Optional[WalletCurrencyType] = Field(
        description="Copay currency",
        sa_column=Column(
            "currency",
            sa.String(15),
            nullable=True,
            index=True,
        ),
    )
    deductible: Optional[Decimal] = Field(
        description="The total cost a user pays on health care before the health plan"
        + " starts covering any expenses",
        nullable=True,
        default=quantize_monetary_number(0),
        sa_column=sa.Column(
            name="deductible",
            type_=sa.DECIMAL(precision=18, scale=2),
            nullable=False,
            comment="The total cost a user pays on health care before the health plan"
            + " starts covering any expenses",
        ),
    )
    out_of_pocket_limit: Optional[Decimal] = Field(
        description="The total amount a user must spend on eligible healthcare"
        + " expenses through copays, coinsurance, or deductibles before"
        + " the health plan starts covering all covered expenses",
        nullable=True,
        default=quantize_monetary_number(0),
        sa_column=sa.Column(
            name="out_of_pocket_limit",
            type_=sa.DECIMAL(precision=18, scale=2),
            nullable=False,
            comment="The total amount a user must spend on eligible healthcare"
            + " expenses through copays, coinsurance, or deductibles before"
            + " the health plan starts covering all covered expenses",
        ),
    )

    def describe_policy(self):
        """Returns a summary of the rules associated with this healthcare policy"""
        descriptions = []
        if self.deductible:
            descriptions.append(f"{self.currency} {self.deductible} deductible")
        if self.out_of_pocket_limit:
            descriptions.append(
                f"{self.currency} {self.out_of_pocket_limit} Out of pocket limt"
            )
        if self.contribution_type == PaymentContributionType.COINSURANCE:
            payer_coinsurance_coverage = round((Decimal(1) - self.coinsurance) * 100, 0)
            descriptions.append(f"Covers {payer_coinsurance_coverage}% of every bill")
        elif self.contribution_type == PaymentContributionType.COPAY:
            descriptions.append("User contributes a fixed amount on every bills")

        return " | ".join(descriptions)

    @validator("coinsurance")
    def validate_coinsurance(cls, v):
        v = quantize_monetary_number(amount=v)
        if v < Decimal(0) or v > Decimal(1):
            raise ValueError(f"Coinsurance must be from 0 to 1. Received {v}")
        return v

    @validator("copay_amount")
    def validate_copay_amount(cls, v):
        v = quantize_monetary_number(amount=v)
        if v < Decimal(0):
            raise ValueError("Copay amount must be greater than 0")
        return v

    @validator("deductible")
    def validate_deductible(cls, v):
        v = quantize_monetary_number(amount=v)
        if v < Decimal(0):
            raise ValueError("Deductible amount must be greater than 0")
        return v

    @validator("out_of_pocket_limit")
    def validate_out_of_pocket_limit(cls, v):
        v = quantize_monetary_number(amount=v)
        if v < Decimal(0):
            raise ValueError("Out of pocket limit must be greater than 0")
        return v


class AbstractUniqueNamedEntity(SQLModel, table=False):
    name: str = Field(
        description="Name of resource/record", unique=True, index=True, nullable=False
    )
    name_chars: str = Field(
        description="Stripped characters of the \
             name without spaces in them",
        sa_column=Column(
            "name_chars", AutoString(70), index=True, nullable=False, unique=True
        ),
    )

    @validator("name_chars")
    def name_chars_validator(cls, v: str) -> str:
        """Returns the stripped lower case name without spaces in them"""
        return v.strip().replace(" ", "").lower()


class AbstractOperatingCountryResource(SQLModel):
    country: OperatingCountryType = Field(description="Country of address")
    line_address: str = Field(
        description="Line address (building no., street name and city)"
    )
    region: str = Field(description="Region/State/Province of address")

    @validator("line_address")
    def line_address_not_empty(cls, v: Optional[str]):
        if not v:
            raise ValueError("Line address must not be empty")
        return v

    # add a validation to field 'region' -> must not be empty
    @validator("region")
    def region_not_empty(cls, v: Optional[str], values: Dict[str, Any]):
        v = str(v).strip()
        if not v:
            raise ValueError("Region must not be empty")
        country = values.get("country")
        # parse country as OperatingCountryType and catch exception
        operating_country_code: OperatingCountryType = OperatingCountryType(
            country
        ).name
        sub_divisions: pycountry.Subdivision = pycountry.subdivisions.get(
            country_code=operating_country_code
        )
        region_matches = [str(i.name) for i in sub_divisions]
        if v not in region_matches:
            error_message = (
                f"Region provided does not match any of the regions for {country}."
                + f" Valid Regions for {country}: {', '.join(region_matches)}"
            )
            raise ValueError(error_message)
        return v
