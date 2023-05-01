"""The :mod:`app.models.organization` module contains a ORMs used to persist and retrieve 
data concerning organizations on HyperSenta
"""
# Author: Christopher Dare

from datetime import datetime
import uuid as uuid_pkg
import orm
import sqlalchemy as sa
from pydantic import EmailStr, validator
from sqlmodel import Column, Field, SQLModel

from app.config.api_config import api_settings

from .abstract import TimeStampedModel
from typing import Optional, Dict, Any


class OrganizationBase(SQLModel):
    name: str = Field(
        description="Business name", unique=True, index=True, nullable=False
    )



class Organization(OrganizationBase, TimeStampedModel, table=True):
    id: Optional[int] = Field(
        sa_column=Column(
            "id",
            sa.INTEGER(),
            index=True,
            autoincrement=True,
            nullable=False,
            primary_key=True,
        ),
        default=None,
    )
    owner_id: uuid_pkg.UUID = Field(
        foreign_key="users.uuid",
        unique=True,
        index=True,
        nullable=False,
        description="User who owns the organization",
    )
    owner_first_name: str = Field(description="Owner's first name", nullable=False)
    owner_last_name: str = Field(description="Owner's last name", nullable=False)
    mobile: Optional[str] = Field(
        regex=r"^\+?1?\d{9,15}$",
        description="International country calling format for owner's phone number",
        nullable=True,
    )
    national_mobile_number: Optional[str] = Field(
        description="National calling format for the owner's phone number",
        nullable=True,
    )
    email: EmailStr = Field(
        description="Owner's email address", index=True, nullable=False
    )
    is_active: bool = Field(
        description="Flag to mark business's active status", default=False
    )
    is_deleted: bool = Field(
        description="Flag to mark business's active status", default=False
    )
    line_address: str = Field(description="Business Line address")
    region: str = Field(description="Region of address")
    country: str = Field(description="Country of address")

    @validator("national_mobile_number", pre=True)
    def validate_national_phone_number(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        from util import parse_mobile_number
        mobile_number = values.get("mobile")
        if not mobile_number:
            return v  # so this can be excluded as an unset property in an update
        national_mobile_number = ""
        try:
            national_mobile_number = parse_mobile_number(
                phone_number=mobile_number, international_format=False
            )
        except phonenumbers.NumberParseException:
            pass
        return national_mobile_number

    # meta properties
    __tablename__ = "organizations"


class OrganizationCreate(OrganizationBase):
    mobile: Optional[str] = None
    national_mobile_number: Optional[str] = None
    email: str
    line_address: Optional[str] = ""
    region: str = ""
    country: str = ""

    @validator("national_mobile_number", pre=True)
    def validate_national_phone_number(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        from utils import parse_mobile_number
        mobile_number = values.get("mobile")
        if not mobile_number:
            return v  # so this can be excluded as an unset property in an update
        national_mobile_number = ""
        try:
            national_mobile_number = parse_mobile_number(
                phone_number=mobile_number, international_format=False
            )
        except phonenumbers.NumberParseException:
            pass
        return national_mobile_number


class OrganizationRead(Organization):
    pass


class OrganizationUpdate(OrganizationBase):
    name: Optional[str] = None
    mobile: Optional[str] = None
    national_mobile_number: Optional[str] = None
    email: Optional[str] = None
    line_address: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    updated_at: datetime = datetime.now()
