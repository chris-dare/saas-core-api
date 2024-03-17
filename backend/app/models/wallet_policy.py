"""The :mod:`app.models.healthcare_policy` module contains a ORMs used to persist and retrieve
data concerning healthcare policyies on HyperSenta
"""
# Author: Christopher Dare

import uuid as uuid_pkg
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

import sqlalchemy as sa
from app.schemas import WalletCurrencyType
from pydantic import EmailStr, validator
from sqlmodel import ARRAY, AutoString, Column, Field, SQLModel, String

from .abstract import (
    AbstractHealthcareWalletPolicy,
    AbstractUniqueNamedEntity,
    TimeStampedModel,
)


class WalletPolicyBase(AbstractHealthcareWalletPolicy):
    name: str = Field(
        description="Name of healthcare wallet policy. Unique for per organization",
        unique=True,
        index=True,
        nullable=False,
    )


class WalletPolicy(
    WalletPolicyBase, TimeStampedModel, AbstractUniqueNamedEntity, table=True
):
    """Health insurance policy. Inherits AbstractHealthcareWalletPolicy
    which provides information shared between about the patient's
    healthcare coverage plan used by both the policy and the wallet
    """

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
    managing_organization_id: uuid_pkg.UUID = Field(
        foreign_key="organizations.uuid",
        index=True,
        nullable=False,
        description="ID of organization managing this policy",
        sa_column_kwargs={
            "comment": "ID of organization managing this policy",
        },
    )
    managing_organization_name: str = Field(
        description="Name of organization managing the wallet"
    )
    name_chars: str = Field(
        description="Stripped characters of the \
             name without spaces in them",
        sa_column=Column(
            "name_chars", AutoString(70), index=True, nullable=False, unique=True
        ),
    )
    description: str = Field(
        description="Description of healthcare wallet policy."
        + "A summary of its rules",
        nullable=False,
    )
    # add a boolean fiend ind
    is_core: Optional[bool] = Field(
        description="Flag to mark policy status as a core policy."
        + " Core policies cannot be deleted",
        default=False,
        sa_column_kwargs={
            "comment": "A flag indicating whether the policy is a core policy."
            + " Core policies cannot be deleted"
        },
    )
    is_deleted: bool = Field(
        description="Flag to mark policy's active status",
        default=False,
        sa_column_kwargs={"comment": "Flag to mark policy's active status"},
    )

    # meta properties
    __tablename__ = "healthcare_policies"
    __table_args__ = (
        sa.UniqueConstraint(
            "name",
            "managing_organization_id",
            name="policy__name__managing_organization_uc",
        ),
        sa.UniqueConstraint(
            "name_chars",
            "managing_organization_id",
            name="policy__name_chars__managing_organization_uc",
        ),
    )


class WalletPolicyCreate(WalletPolicyBase):
    managing_organization_id: uuid_pkg.UUID = Field(
        description="ID of organization managing this policy",
    )

    def name_chars(self) -> str:
        """Returns the stripped lower case name without spaces in them"""
        return self.name.strip().replace(" ", "").lower()


class WalletPolicyRead(WalletPolicyBase):
    name: Optional[str] = None


class WalletPolicyUpdate(WalletPolicyBase):
    name: Optional[str] = None
    updated_at: datetime = datetime.now()
