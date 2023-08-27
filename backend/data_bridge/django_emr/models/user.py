"""The :mod:`django_emr.models.user` module contains ORMs used to persist and retrieve 
data concerning users on Serenity EMR's django backend app
"""
# Author: Christopher Dare


import uuid as uuid_pkg
from datetime import datetime
from typing import Any, Dict, Optional

import phonenumbers
import sqlalchemy as sa
from pydantic import BaseModel, EmailStr, root_validator, validator
from sqlmodel import Column, DateTime, Field, SQLModel, UniqueConstraint

from .abstract import ResourceModel as TimeStampedModel


class UserBase(SQLModel):
    uuid: str = Field(
        default_factory=uuid_pkg.uuid4,
        unique=True,
        index=True,
        nullable=False,
    )
    first_name: str = Field(description="Patient's first name", nullable=False)
    last_name: str = Field(description="Patient's last name", nullable=False)

    mobile: str = Field(
        regex=r"^\+?1?\d{9,15}$",
        index=True,
        nullable=True,
        unique=True,
        description="International country calling format for user's phone number",
    )
    email: EmailStr = Field(
        description="Patient's email address", index=True, nullable=False, unique=True
    )


class User(UserBase, table=True):
    id: Optional[int] = Field(
        sa_column=Column(
            "id",
            sa.INTEGER(),
            index=True,
            autoincrement=True,
            nullable=False,
            primary_key=True,
        ),
        description="Internal database id for Patient table. Not to be exposed to client apps or used as foreign key references",
        default=None,
    )
    national_mobile_number: Optional[str] = Field(
        nullable=True, description="National calling format for the user's phone number"
    )
    password: str = Field(description="User's password", nullable=False)
    date_joined: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_staff: bool = False
    state: str = "new_user"

    @validator("national_mobile_number", pre=True)
    def validate_national_phone_number(
        cls, *, v: Optional[str] = None, values: Dict[str, Any]
    ) -> Any:
        from data_bridge.utils import parse_mobile_number

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

    # meta properties
    __tablename__ = "authenticationmanager_user"
