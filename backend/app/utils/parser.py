"""The :mod:`app.utils.parser` module contains resuable utils for parsing data
"""
# Author: Christopher Dare

from decimal import ROUND_UP, Decimal
from typing import Union

import phonenumbers


def parse_mobile_number(
    phone_number: str, country_code: str = None, international_format: bool = True
) -> str:
    """Transforms a phone number into national or international format"""
    mobile = None
    try:
        if country_code:
            mobile = f"{country_code}{phone_number}"
        else:
            mobile = str(phone_number)
        if mobile[0] != "+":
            mobile = f"+{mobile}"
        mobile = phonenumbers.parse(mobile)
        if international_format:
            mobile = f"+{mobile.country_code}{mobile.national_number}"
        else:  # return number in national format
            mobile = f"{mobile.country_code_source}{mobile.national_number}"
    except phonenumbers.NumberParseException as err:
        raise ValueError("mobile or telephone number is invalid")
    return mobile


def quantize_monetary_number(
    amount: Union[str, Decimal, int], rounding=ROUND_UP
) -> Decimal:
    """Quantizes an amount to 2 decimal places"""
    if amount is None:
        amount = Decimal(0)
    if isinstance(amount, (str, int)):
        amount = Decimal(amount)
    precision = Decimal("0.01")

    return round(amount, 2)

    # alternatively, use the quantize method on the decimal?
    # return amount.quantize(
    #     precision=precision,
    #     rounding=ROUND_UP,
    # )
