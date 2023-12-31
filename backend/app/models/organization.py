"""The :mod:`app.models.organization` module contains a ORMs used to persist and retrieve
data concerning organizations on HyperSenta
"""
# Author: Christopher Dare

import uuid as uuid_pkg
from datetime import datetime
from typing import Any, Dict, Optional

import sqlalchemy as sa
from app.schemas import (
    COUNTRY_CURRENCY_MAP,
    OperatingCountryType,
    OrganizationType,
    OrganizationVerificationType,
    WalletCurrencyType,
)
from pydantic import EmailStr, validator
from sqlmodel import ARRAY, AutoString, Column, Field, SQLModel, String

from .abstract import (
    AbstractOperatingCountryResource,
    AbstractUniqueNamedEntity,
    TimeStampedModel,
)


class OrganizationBase(AbstractOperatingCountryResource):
    name: str = Field(
        description="Business name", unique=True, index=True, nullable=False
    )


class Organization(
    OrganizationBase, TimeStampedModel, AbstractUniqueNamedEntity, table=True
):
    pk: Optional[int] = Field(
        sa_column=Column(
            "pk",
            sa.INTEGER(),
            index=True,
            autoincrement=True,
            nullable=False,
            primary_key=True,
        ),
        default=None,
    )
    owner_id: uuid_pkg.UUID = Field(
        foreign_key="users.uuid",
        unique=True,
        index=True,
        nullable=False,
        description="User who owns the organization",
    )
    country: str = Field(description="Country of address")
    default_wallet_currency: WalletCurrencyType = Field(
        description="Wallet currency. If not set, it defaults to \
            the country of operation",
        sa_column=Column(
            "default_wallet_currency",
            sa.String(15),
            nullable=False,
            index=False,
        ),
    )
    email: Optional[EmailStr] = Field(
        description="Owner's email address", index=True, nullable=True
    )
    is_deleted: bool = Field(
        description="Flag to mark business's active status", default=False
    )
    is_verified: bool = Field(
        description="Flag to mark business's verification status", default=False
    )
    line_address: Optional[str] = Field(
        description="Business Line address", nullable=False
    )
    organization_type: OrganizationType = Field(description="Type of organization")
    owner_first_name: str = Field(description="Owner's first name", nullable=False)
    owner_last_name: str = Field(description="Owner's last name", nullable=False)
    region: str = Field(description="Region of address")
    verification_id: str = Field(description="ID of verification record", nullable=True)
    verification_document: str = Field(
        description="Name of uploaded document used to verify the organization",
        nullable=True,
    )
    verification_mode_types: list[OrganizationVerificationType] = Field(
        description="Methods used to verify the organization",
        nullable=True,
        sa_column=Column(ARRAY(String)),
    )
    name: str = Field(
        description="Business name",
        sa_column=Column(
            "name", AutoString(70), index=True, nullable=False, unique=True
        ),
    )
    created_by_id: uuid_pkg.UUID = Field(
        foreign_key="users.uuid",
        index=True,
        nullable=False,
        description="User who created the organization",
    )
    created_by_name: str = Field(
        description="Name of user who created the organization", nullable=False
    )

    @validator("name_chars")
    def name_chars_validator(cls, v: str) -> str:
        """Returns the stripped lower case name without spaces in them"""
        return v.strip().replace(" ", "").lower()

    # meta properties
    __tablename__ = "organizations"
    # Ensure case-insensitive uniqueness for the 'name' column
    # __table_args__ = (
    #     sa.UniqueConstraint(sa.func.lower("name"), name="unique_name_case_insensitive"),
    # )


class OrganizationCreate(OrganizationBase):
    country: OperatingCountryType = Field(
        description="Country of the indicated line address",
    )
    # default_wallet_currency: Optional[WalletCurrencyType] = Field(
    #     description="Wallet currency. Defaults to (and currently limited to) currency \
    #     of operating country. e.g. Ghana is GHS"
    # )
    email: str = Field(description="Email address of organization (or its owner)")
    line_address: Optional[str] = Field(
        default="", description="Line address of organization"
    )
    organization_type: OrganizationType = Field(description="Type of organization")
    owner_id: Optional[uuid_pkg.UUID] = Field(
        description="User id of the organization's owner",
        default=None,
    )
    region: str = Field(
        default="",
        description="Region of the indicated line address",
    )

    def name_chars(self) -> str:
        """Returns the stripped lower case name without spaces in them"""
        return self.name.strip().replace(" ", "").lower()


class OrganizationRead(OrganizationBase):
    uuid: uuid_pkg.UUID = Field(default="Unique resource identifier")
    country: str
    email: str
    is_verified: bool = Field(
        description="Flag to mark business's verification status", default=False
    )
    line_address: str
    organization_type: OrganizationType
    owner_first_name: str
    owner_last_name: str
    region: str
    default_wallet_currency: WalletCurrencyType = Field(
        description="Default Wallet currency"
    )
    verification_document: Optional[str] = Field(
        description="Link to uploaded verification document"
    )


class OrganizationUpdate(OrganizationBase):
    country: Optional[str] = None
    email: Optional[str] = None
    line_address: Optional[str] = None
    name: Optional[str] = None
    region: Optional[str] = None
    updated_at: datetime = datetime.now()
