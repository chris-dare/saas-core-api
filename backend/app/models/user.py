"""The :mod:`app.models.user` module contains a ORMs used to persist and retrieve 
data concerning users on HyperSenta
"""
# Author: Christopher Dare


import uuid as uuid_pkg
from datetime import datetime, date
from typing import Any, Dict, Optional

import phonenumbers
import sqlalchemy as sa
from pydantic import BaseModel, EmailStr, root_validator, validator
from sqlmodel import Column, DateTime, Field, SQLModel

from app.schemas import AdministrativeGender, Token, NationalIdType


from .abstract import TimeStampedModel


class UserBase(SQLModel):
    first_name: str = Field(description="User's first name", nullable=False)
    last_name: str = Field(description="User's last name", nullable=False)
    mobile: str = Field(
        regex=r"^\+?1?\d{9,15}$",
        index=True,
        unique=True,
        description="International country calling format for user's phone number (E164 format)",
    )
    email: Optional[EmailStr] = Field(
        description="User's email address", index=True, nullable=True, unique=True
    )
    birth_date: Optional[date] = Field(
        description="User's date of birth", nullable=True, default=None
    )
    gender: Optional[AdministrativeGender] = Field(
        description="User's gender", nullable=True, default=None,
    )



class User(UserBase, TimeStampedModel, table=True):
    id: Optional[int] = Field(
        sa_column=Column(
            "id",
            sa.INTEGER(),
            index=True,
            autoincrement=True,
            nullable=False,
            primary_key=True,
        ),
        description="Internal database id for User table. Not to be exposed to client apps or used as foreign key references",
        default=None,
    )
    full_name: Optional[str] = Field(description="User's full name", index=True, nullable=False)
    national_mobile_number: Optional[str] = Field(
        nullable=True, description="National calling format for the user's phone number"
    )
    nationality: Optional[str] = Field(
        description="Country of user's nationality", nullable=True, default=None
    )
    national_id: Optional[str] = Field(
        description="User's national ID number", nullable=True, default=None
    )
    national_id_type: Optional[NationalIdType] = Field(
        description="User's national ID type", nullable=True, default=None
    )
    is_active: bool = Field(
        description="Flag to mark user's active status. To be active a user's mobile number and national ID must be verified",
        default=False
    )
    is_identity_verified: bool = Field(
        description="Flag to mark user's identity verification status", default=False
    )
    is_superuser: bool = Field(
        description="Flag to mark user's superuser status", default=False
    )
    password: Optional[str] = Field(description="Hash of user's password/pin")
    last_login: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True)), nullable=True
    )
    updated_at: datetime = datetime.now()

    @validator("national_mobile_number", pre=True)
    def validate_national_phone_number(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        from app.utils import parse_mobile_number
        mobile_number = values.get("mobile")
        if not mobile_number:
            return v  # since mobile is optional, return None or "" if not present
        national_mobile_number = ""
        try:
            national_mobile_number = parse_mobile_number(
                phone_number=mobile_number, international_format=False
            )
        except phonenumbers.NumberParseException:
            # TODO: log error on sentry
            pass
        return national_mobile_number

    @validator("full_name", pre=True)
    def validate_full_name(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        return f"{values.get('first_name')} {values.get('last_name')}"

    @validator("nationality", pre=True)
    def validate_nationality(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if v:
            import pycountry
            is_valid_country = False
            for country in pycountry.countries:
                if country.name == v:
                    is_valid_country = True
                    break
            if not is_valid_country:
                raise ValueError("Invalid country name")
        return v


    # meta properties
    __tablename__ = "users"


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(description="Hash of user's password or pin", default=None)
    mobile: str
    first_name: str = Field(description="User's first name", nullable=False,)
    last_name: str = Field(description="User's last name", nullable=False,)
    # if org name is available, should be used to create organization for user

    @validator("password")
    def set_password(cls, v: str, values: Dict[str, Any]) -> Any:
        from app.utils import make_password
        # ensure that only the hashed password of the user is saved.
        # TODO: Move this behavior to the User object manager
        return make_password(raw_password=v) if v else None


class UserRead(UserBase, TimeStampedModel):
    full_name: str = Field(index=True, nullable=False)
    is_active: bool
    last_login: Optional[datetime] = None
    national_mobile_number: Optional[str] = Field(
        description="National calling format for the user's phone number"
    )

class NewUserRead(UserRead, Token):
    """Model with access token details to authenticate new users before verifying their email
    """
    pass

class UserPublicRead(BaseModel):
    """Used to check the user's active status
    """
    is_active: bool = Field(
        description="Flag to mark user's active status", default=False
    )

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    updated_at: datetime = datetime.now()
    mobile: Optional[str] = Field(
        regex=r"^\+?1?\d{9,15}$",
        index=True,
        nullable=True,
        unique=True,
        description="International country calling format for user's phone number (E164 format)",
    )

    @validator("updated_at", pre=True)
    def validate_updated_at(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        # set user's full name when first and last names are present
        # requirements for full name will differ per use case e.g. create (required) vs update (not required)
        first_name = values.get("first_name")
        last_name = values.get("last_name")
        if first_name and last_name:
            return f"{first_name} {last_name}"
        else:
            return v