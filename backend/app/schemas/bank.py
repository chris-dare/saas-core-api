"""The :mod:`app.models.bank` module contains models used to
represent banking information from payment service providers
data concerning SubAccounts on Serenity
"""
# Author: Christopher Dare
from pydantic import BaseModel


class ResolvedBankAccount(BaseModel):
    account_number: str
    account_name: str
    bank_id: str


class PaystackBank(BaseModel):
    name: str
    slug: str
    code: str
    active: str
    country: str
    currency: str
    type: str
