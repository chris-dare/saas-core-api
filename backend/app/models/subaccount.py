"""The :mod:`app.models.subaccount` module contains a ORMs used to persist and retrieve
data concerning SubAccounts on HyperSenta
"""
# Author: Christopher Dare


import uuid as uuid_pkg
from datetime import datetime, timedelta
from typing import Optional, Union
from decimal import Decimal

import phonenumbers
import sqlalchemy as sa
from pydantic import BaseModel, EmailStr, validator
from sqlmodel import Column, DateTime, Field, SQLModel

from app.core.config import settings

from .abstract import TimeStampedModel


class SubAccountBase(SQLModel):
    business_name: str = Field(
        description="Name of business for subaccount", unique=False, index=True, nullable=False
    )
    settlement_bank_code: str = Field(
        description="Bank Code for the bank",
        default="",
    )
    account_number: str = Field(
        description="Code of the bank account to be used to charge the customer",
        default="",
    )
    description: str = Field(
        description="An arbitrary string attached to the object. Often useful for displaying to users",
        default="",
    )
    primary_contact_email: EmailStr = Field(
        description="A contact email for the settlement account", unique=False, index=True, nullable=False
    )
    primary_contact_name: str = Field(
        description="A name for the contact person for this subaccount", unique=False, index=True, nullable=True
    )
    primary_contact_phone: str = Field(
        description="User's phone number", unique=False, index=True, nullable=True
    )


class SubAccount(SubAccountBase, TimeStampedModel, table=True):
    id: Optional[int] = Field(
        sa_column=Column(
            "id",
            sa.INTEGER(),
            index=True,
            autoincrement=True,
            nullable=False,
            primary_key=True,
        ),
        description="Internal database id for SubAccount table. Not to be exposed to client apps or used as foreign key references",
    )
    uuid: uuid_pkg.UUID = uuid_pkg.uuid4()
    owner_id: uuid_pkg.UUID = Field(
        foreign_key="users.uuid",
        description="Account owner (user)", nullable=False, index=True
    )
    organization_id: uuid_pkg.UUID = Field(
        foreign_key="organizations.uuid",
        index=True,
        nullable=False,
        description="Account owner's organization",
    )
    percentage_charge: Decimal = Field(
        description="Percentage of a transaction to be settled to the account",
        sa_column=sa.DECIMAL(precision=5, scale=2)
    )
    is_active: Optional[bool] = Field(
        default=True,
        description="Status on whether the subaccount is active or not",
    )
    is_deleted: Optional[bool] = Field(
        default=False,
        description="Status on whether the subaccount has been deleted or not",
    )
    is_verified: Optional[bool] = Field(
        default=False,
        description="Status on whether the subaccount has been verified or not",
    )
    is_primary: Optional[bool] = Field(
        default=False,
        description="Status on whether the subaccount is the primary account for the organization",
    )
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    # meta properties
    __tablename__ = "subaccounts"


# Properties to receive via API on creation
class SubAccountCreate(SubAccountBase):
    description: Optional[str] = ""
    pass

class SubAccountRead(SubAccountBase, TimeStampedModel):
    uuid: uuid_pkg.UUID
    organization_id: uuid_pkg.UUID
    owner_id: str
    created_at: datetime
    updated_at: datetime
    owner_id: uuid_pkg.UUID
    percentage_charge: Decimal

class SubAccountUpdate(SubAccountBase, TimeStampedModel):
    updated_at: datetime = datetime.now()
    pass