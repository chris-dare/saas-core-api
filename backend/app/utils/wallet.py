"""The :mod:`app.utils.wallet` module contains resuable utils for wallet operations
"""
# Author: Christopher Dare

from app import schemas


def get_country_currency(country: schemas.OperatingCountryType, raise_exception=True):
    """Get currency for country

    Args:
        country (schemas.OperatingCountryType): Country to get currency for

    Returns:
        str: Currency for country
    """

    currency = schemas.COUNTRY_CURRENCY_MAP.get(country, None)
    if not currency and raise_exception:
        raise ValueError(
            f"Could not resolve currency for country {country}."
            + " Is this country supported by Serenity?"
        )
    return currency
