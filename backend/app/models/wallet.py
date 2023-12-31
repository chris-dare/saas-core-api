"""The :mod:`app.models.wallet` module contains a ORMs used to persist and retrieve
data concerning wallets on HyperSenta
"""
# Author: Christopher Dare

import uuid as uuid_pkg
from datetime import datetime
from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from app.schemas import WalletCurrencyType, WalletStatusType
from app.utils import quantize_monetary_number
from sqlmodel import Column, Field, SQLModel

from .abstract import AbstractHealthcareWalletPolicy, TimeStampedModel


class WalletBase(SQLModel):
    managing_organization_id: Optional[uuid_pkg.UUID] = Field(
        description="ID of organization managing this wallet"
    )
    currency: WalletCurrencyType = Field(description="Wallet currency")


class Wallet(WalletBase, TimeStampedModel, AbstractHealthcareWalletPolicy, table=True):
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
    # wallet statuses should be explicitly activated and not be done by default
    # hence the default status for a wallet is "CREATED" instead of "ACTIVE"
    status: WalletStatusType = Field(
        description="Status of wallet",
        sa_column=Column(
            "status",
            sa.String(15),
            nullable=False,
            index=True,
        ),
        default=WalletStatusType.CREATED,
    )
    balance: Decimal = Field(
        description="The remaining balance of the wallet",
        default=quantize_monetary_number(0),
    )
    currency: WalletCurrencyType = Field(
        description="Wallet currency",
        sa_column=Column(
            "currency",
            sa.String(15),
            nullable=False,
            index=True,
        ),
    )
    description: Optional[str] = Field(
        description="", unique=True, default="", index=True, nullable=False
    )
    managing_organization_id: uuid_pkg.UUID = Field(
        foreign_key="organizations.uuid",
        index=True,
        nullable=False,
        description="ID of organization managing this wallet",
    )
    managing_organization_name: str = Field(
        description="Name of organization managing the wallet"
    )
    # if wallet table is amended, ensure that the policy id fk...
    # maintains the constaint name `wallet__policy_id__fk` in schema_extra
    policy_id: uuid_pkg.UUID = Field(
        foreign_key="healthcare_policies.uuid",
        index=True,
        nullable=True,
        description="ID of current healthcare policy applied to the wallet",
        sa_column_kwargs={
            "comment": "ID of current healthcare policy applied to the wallet",
        },
        schema_extra={"constraint_name": "wallet__policy_id__fk"},
    )
    policy_name: str = Field(
        description="Name of current healthcare policy applied to the wallet",
        nullable=True,
        index=True,
        sa_column_kwargs={
            "comment": "Name of current healthcare policy applied to the wallet",
        },
    )
    owner_id: uuid_pkg.UUID = Field(
        foreign_key="users.uuid",
        index=True,
        nullable=False,
        description="User who owns the wallet",
    )
    owner_name: str = Field(description="Name of user who owns this wallet")
    owner_mobile: str = Field(description="Mobile number of user who owns this wallet")

    # meta properties
    __tablename__ = "wallets"
    __table_args__ = (
        sa.UniqueConstraint(
            "owner_id",
            "managing_organization_id",
            name="wallet__owner_managing_organization_uc",
        ),
    )


class WalletCreate(WalletBase):
    managing_organization_id: Optional[uuid_pkg.UUID] = Field(
        description="ID of organization managing this wallet"
    )
    currency: WalletCurrencyType = Field(description="Wallet currency")
    owner_id: uuid_pkg.UUID = Field(description="ID of User who owns the wallet")


class WalletRead(WalletBase, AbstractHealthcareWalletPolicy):
    uuid: uuid_pkg.UUID = Field(default="Unique resource identifier")
    description: Optional[str] = None
    balance: Decimal = Field(
        description="Wallet balance",
        default=quantize_monetary_number(0),
        sa_column=sa.Column(
            name="balance",
            type_=sa.DECIMAL(precision=18, scale=2),
            nullable=False,
            comment="Wallet balance",
        ),
    )
    currency: WalletCurrencyType = Field(description="Wallet currency")
    managing_organization_id: uuid_pkg.UUID = Field(
        description="ID of organization managing this wallet"
    )
    managing_organization_name: str = Field(
        description="Name of organization managing the wallet"
    )
    owner_id: uuid_pkg.UUID = Field(description="ID of User who owns the wallet")
    owner_name: str = Field(description="Name of user who owns this wallet")
    policy_id: uuid_pkg.UUID = Field(
        description="ID of healthcare policy applied to the wallet"
    )
    policy_name: str = Field(
        description="Name of current healthcare policy applied to the wallet",
    )
    status: WalletStatusType = Field(
        description="Status of wallet",
    )


class WalletUpdate(WalletBase):
    name: Optional[str] = None
    updated_at: datetime = datetime.now()
