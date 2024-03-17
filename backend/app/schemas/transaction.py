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

from enum import Enum

from pydantic import validator


class TransactionStatusType(str, Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"


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
