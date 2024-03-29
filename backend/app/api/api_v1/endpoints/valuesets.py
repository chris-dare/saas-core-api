import datetime
from typing import Any, Optional

import pycountry
from app import schemas, utils
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/administrative-gender", response_model=schemas.GenericValueset)
def read_administrative_gender() -> Any:
    """
    Retrieves a list of Administrative genders
    """
    return schemas.GenericValueset(
        name="AdministrativeGender",
        choices=utils.get_enum_as_list(schemas.AdministrativeGender),
    )
    return paginate(users)


@router.get("/countries", response_model=schemas.GenericValueset)
def read_countries() -> Any:
    """
    Retrieves a list of countries
    """
    return schemas.GenericValueset(
        name="Countries", choices=[country.name for country in pycountry.countries]
    )


@router.get("/operating-country-regions", response_model=list[schemas.GenericValueset])
def read_operating_country_regions(
    country: Optional[schemas.OperatingCountryType] = None,
) -> Any:
    """
    Retrieves a values of regions for countries in which Serenity operates.
    You may query by country name e.g. 'Ghana'
    When writing data, use the name of country and a suitable region as payload values.
    Descriptions are only to provide clarity to users/developers where necessary
    """
    return schemas.OperatingCountryType.as_valueset(country=country)


@router.get("/national-id-types", response_model=schemas.GenericValueset)
def read_national_id_types() -> Any:
    """
    Retrieves a list of national ID types
    """
    return schemas.GenericValueset(
        name="NationalIdType", choices=utils.get_enum_as_list(schemas.NationalIdType)
    )
