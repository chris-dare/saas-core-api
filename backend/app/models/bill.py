"""The :mod:`app.models.bill` module contains ORMs used to persist and retrieve
data concerning bills generated

A bill typically has the following information:
1. Service or product name
2. User charged
3. Status
4. Related transaction where the bill was paid for - if the bill has been paid
5. Organization issuing the bill
6. Product charged
7. Comments
8. Unit price
9. Quantity
10. Date generated
11. Date paid
12. Date payment was settled
13. Currency
14. Total_amount
"""
# Author: Chris Dare

from datetime import datetime
import uuid as uuid_pkg
import orm
import sqlalchemy as sa
from pydantic import EmailStr, validator
from sqlmodel import Column, Field, SQLModel, UniqueConstraint

from decimal import Decimal
from enum import Enum, IntEnum

from app.config.api_config import api_settings

from .abstract import TimeStampedModel
from typing import Optional, Dict, Any


class BillStatusType(str, Enum):
    BILLABLE = 'online'
    ABORTED = 'pre-recorded'
    BILLED = 'hybrid'


class CurrencyType(str, Enum):
    GHS = "GHS"
    USD = "USD"


class BillBase(SQLModel):
    pass


class Bill(BillBase, TimeStampedModel, table=True):
    id: Optional[int] = Field(
        sa_column=Column(
            "id",
            sa.INTEGER(),
            index=True,
            autoincrement=True,
            nullable=False,
            primary_key=True,
        ),
        default=None,
    )
    status: Optional[BillStatusType] = BillStatusType.BILLABLE
    category: Optional[str] = None
    customer_name: str = Field(
        description="Instructor name", unique=False, index=True, nullable=False
    )
    customer_email: EmailStr = Field(
        description="User's email address", unique=False, index=True, nullable=False
    )
    customer_mobile: EmailStr = Field(
        description="User's phone number", unique=False, index=True, nullable=True
    )
    customer_id: uuid_pkg.UUID = Field(
        foreign_key="users.uuid",
        index=True,
        nullable=False,
        description="The ID of the customer who will be billed",
    )
    transaction_id: uuid_pkg.UUID = Field(
        foreign_key="transactions.uuid",
        index=True,
        nullable=True,
        description="Related successful transaction",
    )
    organization_name: str = Field(
        description="Business name", unique=False, index=True, nullable=False
    )
    organization_id: uuid_pkg.UUID = Field(
        foreign_key="organizations.uuid",
        index=True,
        nullable=False,
        description="User who owns the Bill",
    )
    service_or_product_name: str = Field(
        description="Name of product user is being charged for", nullable=False
    )
    product_id: uuid_pkg.UUID = Field(
        foreign_key="events.uuid", # update this with the FK to your product
        index=True,
        nullable=False,
        description="Product the customer is being charged for",
    )
    currency: Optional[CurrencyType] = Field(
        description="Currency of the bill. If none is provided, the customer's currency is used",
        default=CurrencyType.USD,
    )
    total_amount: Decimal
    charge: Decimal = Field(
        description="The amount to be charged to the customer. If none is provided, the total amount is used",
    )
    unit_price: Decimal
    quantity: Optional[int] = 1
    description: Optional[str] = Field(
        description="Extra notes about the bill", unique=False, index=False, nullable=True
    )
    paid_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None

    def cancel(self):
        self.status = BillStatusType.ABORTED
        self.canceled_at = datetime.now()
        # TODO: Create bill action history and return
        _ = None
        return self, _

    # meta properties
    __tablename__ = "bills"


class BillCreate(BillBase):
    product_id: uuid_pkg.UUID = Field(
        description="The ID of the product/service being sold",
    )
    description: Optional[str] = Field(
        description="An arbitrary string attached to the object. Often useful for displaying to users",
        default="",
    )
    quantity: Optional[int] = Field(
        description="Number of units of the product/service being sold. \
            If none is provided, the default is 1",
        default=1,
    )


class BillRead(BillBase):
    uuid: uuid_pkg.UUID
    organization_id: uuid_pkg.UUID
    customer_id: uuid_pkg.UUID
    product_id: uuid_pkg.UUID
    status: Optional[BillStatusType]
    customer_name: str
    customer_email: str
    customer_mobile: Optional[str] = None
    organization_name: str
    service_or_product_name: str
    currency: Optional[CurrencyType] = CurrencyType.USD
    total_amount: Optional[Decimal] = 0
    unit_price: Optional[Decimal] = 0
    quantity: Optional[int] = 0
    paid_at: Optional[datetime] = None
    created_at: datetime


class BillUpdate(BillBase):
    service_or_product_name: Optional[str] = None
    status: Optional[BillStatusType] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = datetime.now()
    end_date: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
