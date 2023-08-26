"""The :mod:`app.utils.bank` module contains resuable utils for messaging users via SMS or email
"""
# Author: Christopher Dare

import httpx

from app.core.config import settings
from app.schemas import PaymentServiceProviderType, PaystackBank, ResolvedBankAccount


async def resolve_account_number(account_number: str, bank_code: str):
    response = await httpx.AsyncClient().get(
        f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}",
        headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
    )
    if response.status_code == 200 and response.json().get("status"):
        resolved_bank_account = ResolvedBankAccount(**response.json().get("data"))
    else:
        try:
            error_message = response.json().get("message")
        except Exception:
            error_message = "Technical error occurred!"
        raise ValueError(f"Could not resolve account: {error_message}")
    return resolved_bank_account


async def get_bank_list(
    country: str,
    items_per_page: int = 100,
    provider: PaymentServiceProviderType = PaymentServiceProviderType.PAYSTACK,
):
    if items_per_page > 100:
        raise ValueError("items_per_page must be less than 100")
    response = await httpx.AsyncClient().get(
        f"https://api.paystack.co/bank?country={country}&perPage={items_per_page}",
        headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
    )
    banks = []
    if response.status_code == 200 and response.json().get("status"):
        for bank in response.json().get("data"):
            banks.append(PaystackBank(**bank))
    else:
        raise ValueError("Could not resolve account")
    return banks
