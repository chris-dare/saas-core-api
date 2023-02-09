"""The :mod:`app.models.transaction` module contains ORMs used to persist and retrieve
data concerning transactions for bil payments

A transaction typically has the following information:
1. Related bill
2. User charged
3. Status
4. Amount charged
5. Organization issuing the transaction
6. Product charged
7. Comments
8. Mode of payment
9. Currency
10. Date generated
11. Date paid
12. Date payment was settled
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

from app.core.config import settings
from app.utils.parser import parse_mobile_number

from .abstract import TimeStampedModel
from typing import Optional, Dict, Any

import httpx


class TransactionStatusType(str, Enum):
    SUCCESS = 'SUCCESS'
    PENDING = 'PENDING'
    FAILED = 'FAILED'
    CANCELED = 'CANCELED'
    REFUNDED = 'REFUNDED'


class CurrencyType(str, Enum):
    GHS = "GHS"
    USD = "USD"


class PaymentServiceProviderType(str, Enum):
    PAYSTACK = "PAYSTACK"
    # TODO: Add more payment service providers


class PaymentChannelType(str, Enum):
    CARD = "CARD"
    BANK = "BANK"
    MOBILE_MONEY = "MOBILE_MONEY"
    USSD = "USSD"
    QR = "QR"


class MobileMoneyProvider(str, Enum):
    MTN = "MTN"
    VODAFONE = "VODAFONE"
    AIRTELTIGO = "AIRTELTIGO"


class ModeOfPaymentType(str, Enum):
    MOBILE_MONEY = "MOBILE_MONEY"
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD = "CARD"


class TransactionBase(SQLModel):
    pass


class Transaction(TransactionBase, TimeStampedModel, table=True):
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
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        unique=True,
        index=True,
        nullable=False,
        description="Unique identifier for the transaction. \
            Also used as the transaction reference in the payment gateway",
    )
    status: Optional[TransactionStatusType] = TransactionStatusType.PENDING
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
    description: Optional[str] = Field(
        description="An arbitrary string attached to the object. Often useful for displaying to users",
        default="",
    )
    bill_id: uuid_pkg.UUID = Field(
        foreign_key="bills.uuid",
        index=True,
        nullable=True,
        description="Related successful transaction",
    )
    service_or_product_name: str = Field(
        description="Name of product user is being charged for", nullable=False
    )
    product_id: uuid_pkg.UUID = Field(
        foreign_key="courses.uuid", # update this with the FK to your product
        index=True,
        nullable=False,
        description="Product the customer is being charged for",
    )
    currency: Optional[CurrencyType] = Field(
        description="Currency of the transaction. If none is provided, the customer's currency is used",
        default=CurrencyType.USD,
    )
    payment_service_provider: Optional[PaymentServiceProviderType] = Field(
        description="Payment service provider (PSP) used to process the transaction. If none is provided, the default is PAYSTACK",
        default=PaymentServiceProviderType.PAYSTACK,
    )
    checkout_url: Optional[str] = Field(
        description="Checkout URL for the transaction",
        default="",
    )
    access_code: Optional[str] = Field(
        description="PSP's access code for the transaction",
        default="",
    )
    mode_of_payment: Optional[ModeOfPaymentType] = Field(
        description="Mode of payment used to process the transaction. If none is provided, the default is MOBILE_MONEY",
        default=ModeOfPaymentType.MOBILE_MONEY,
    )
    amount: Decimal = Field(
        description="Amount to be charged to the customer. If none is provided, the default is 0",
    )
    card_ending_digits: Optional[str] = Field(
        description="Last 4 digits of the card used to charge the customer",
        default="",
    )
    mobile_money_phone_number: Optional[str] = Field(
        description="Phone number of the mobile money account to be charged",
        default="",
    )
    mobile_money_provider: Optional[MobileMoneyProvider] = Field(
        description="Mobile money provider to be used to charge the customer",
        default="",
    )
    bank_account_number: Optional[str] = Field(
        description="Bank account number to be used to charge the customer",
        default="",
    )
    bank_account_code: Optional[str] = Field(
        description="Code of the bank account to be used to charge the customer",
        default="",
    )
    bank_account_name: Optional[str] = Field(
        description="Name of the bank account to be used to charge the customer",
        default="",
    )
    # reference: Optional[str] = Field(
    #     description="External transaction reference",
    #     default="",
    # )
    paid_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None

    def initialize(self,
        payment_service_provider: PaymentServiceProviderType = PaymentServiceProviderType.PAYSTACK,
        payment_channels: list[PaymentChannelType] = [PaymentChannelType.CARD, PaymentChannelType.MOBILE_MONEY]):
        """intialize a transaction via the payment service provider"""
        status = False
        if payment_service_provider == PaymentServiceProviderType.PAYSTACK:

            response = httpx.post("https://api.paystack.co/transaction/initialize",
                     json={"email": str(self.customer_email), "amount": str(self.amount*100), "callback_url": str(settings.CLIENT_APP_HOST)}, 
                     headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}', 'Content-Type': 'application/json'})
            if response.status_code == 200 and response.json().get("status"):
                self.access_code = response.json().get("data").get("access_code")
                self.checkout_url = response.json().get("data").get("authorization_url")
        else:
            raise ValueError("Unsupported payment service provider")

    def cancel(self):
        self.status = TransactionStatusType.FAILED
        self.canceled_at = datetime.now()
        # TODO: Create transaction action history and return
        _ = None
        return self, _

    # meta properties
    __tablename__ = "transactions"


class TransactionCreate(TransactionBase):
    bill_id: uuid_pkg.UUID = Field(
        description="The ID of the product/service being sold",
    )
    payment_service_provider = Field(
        description="Payment service provider (PSP) used to process the transaction.\
            If none is provided, the default is PAYSTACK",
        default=PaymentServiceProviderType.PAYSTACK,
    )
    description: Optional[str] = Field(
        description="An arbitrary string attached to the object. Often useful for displaying to users",
        default="",
    )


class TransactionRead(TransactionBase):
    uuid: uuid_pkg.UUID
    customer_id: uuid_pkg.UUID
    product_id: uuid_pkg.UUID
    status: Optional[TransactionStatusType]
    customer_name: str
    customer_email: str
    customer_mobile: Optional[str] = None
    service_or_product_name: str
    currency: Optional[CurrencyType] = CurrencyType.USD
    amount: Optional[Decimal] = 0
    checkout_url: Optional[str] = ""
    access_code: Optional[str] = ""


class TransactionUpdate(TransactionBase):
    status: Optional[TransactionStatusType] = None
    updated_at: Optional[datetime] = datetime.now()
