"""The :mod:`app.models.country` module contains models used to
represent residential information of an entity such as a user or an organization
"""
# Author: Christopher Dare
from typing import Any, Dict, Optional

import pycountry
from pydantic import BaseModel, Field, validator

from .choices import OperatingCountryType


class OperatingCountryResourceSchema(BaseModel):
    country: OperatingCountryType = Field(description="Country of address")
    line_address: str = Field(
        description="Line address (building no., street name and city)"
    )
    region: str = Field(description="Region/State/Province of address")

    @validator("line_address")
    def line_address_not_empty(cls, v: Optional[str]):
        if not v:
            raise ValueError("Line address must not be empty")
        return v

    # add a validation to field 'region' -> must not be empty
    @validator("region")
    def region_not_empty(cls, v: Optional[str], values: Dict[str, Any]):
        v = str(v).strip()
        if not v:
            raise ValueError("Region must not be empty")
        country = values.get("country")
        # parse country as OperatingCountryType and catch exception
        operating_country_code: OperatingCountryType = OperatingCountryType(
            country
        ).name
        sub_divisions: pycountry.Subdivision = pycountry.subdivisions.get(
            country_code=operating_country_code
        )
        region_matches = [str(i.name) for i in sub_divisions]
        if v not in region_matches:
            error_message = (
                f"Region provided does not match any of the regions for {country}."
                + f" Valid Regions for {country}: {', '.join(region_matches)}"
            )
            raise ValueError(error_message)
        return v
