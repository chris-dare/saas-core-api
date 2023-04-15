"""The :mod:`app.utils.bank` module contains resuable utils for messaging users via SMS or email
"""
# Author: Christopher Dare

import httpx
from app.core.config import settings
from app.models import ResolvedBankAccount
from app.models import PaystackBank, PaymentServiceProviderType

def resolve_account_number(account_number: str, bank_code: str):
    response = httpx.get(f'https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}',
        headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'})
    if response.status_code == 200 and response.json().get("status"):
        resolved_bank_account = ResolvedBankAccount(
            **response.json().get("data")
        )
    else: raise ValueError("Could not resolve account")
    return resolved_bank_account

def get_bank_list(country: str, items_per_page: int = 100, provider: PaymentServiceProviderType = PaymentServiceProviderType.PAYSTACK):
    if items_per_page > 100:
        raise ValueError("items_per_page must be less than 100")
    response = httpx.get(f'https://api.paystack.co/bank?country={country}&perPage={items_per_page}',
        headers={'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'})
    banks = []
    if response.status_code == 200 and response.json().get("status"):
        for bank in response.json().get("data"):
            banks.append(
                PaystackBank(**bank)
            )
    else: raise ValueError("Could not resolve account")
    return banks

