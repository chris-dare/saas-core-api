import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
import pycountry

from app import schemas
from app import utils

router = APIRouter()


@router.get("/administrative-gender", response_model=schemas.GenericValueset)
def read_administrative_gender(
) -> Any:
    """
    Retrieves a list of Administrative genders
    """
    return schemas.GenericValueset(name="AdministrativeGender", choices=utils.get_enum_as_list(schemas.AdministrativeGender))
    return paginate(users)

@router.get("/countries", response_model=schemas.GenericValueset)
def read_countries() -> Any:
    """
    Retrieves a list of countries
    """
    return schemas.GenericValueset(name="Countries", choices=[country.name for country in pycountry.countries])

@router.get("/national-id-types", response_model=schemas.GenericValueset)
def read_national_id_types() -> Any:
    """
    Retrieves a list of national ID types
    """
    return schemas.GenericValueset(name="NationalIdType", choices=utils.get_enum_as_list(schemas.NationalIdType))
