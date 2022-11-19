"""The :mod:`app.models.OTP` module contains a ORMs used to persist and retrieve 
data concerning OTPs on HyperSenta
"""
# Author: Christopher Dare


import uuid as uuid_pkg
from datetime import datetime, timedelta
from typing import Optional, Union

import phonenumbers
import sqlalchemy as sa
from pydantic import EmailStr, validator
from sqlmodel import Column, DateTime, Field, SQLModel

from app.core.config import settings

from .abstract import TimeStampedModel


class OTPBase(SQLModel):
    user_id: uuid_pkg.UUID = Field(
        description="User's public UUID", nullable=False, index=True
    )
    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
        ),
        description="OTP expiry datetime",
    )


class OTP(OTPBase, TimeStampedModel, table=True):
    id: Optional[int] = Field(
        sa_column=Column(
            "id",
            sa.INTEGER(),
            index=True,
            autoincrement=True,
            nullable=False,
            primary_key=True,
        ),
        description="Internal database id for OTP table. Not to be exposed to client apps or used as foreign key references",
    )
    code: str = Field(description="OTP code", nullable=False)

    # meta properties
    __tablename__ = "otp"


# Properties to receive via API on creation
class OTPCreate(OTPBase):
    uuid: uuid_pkg.UUID = uuid_pkg.uuid4()
    expires_at: datetime = datetime.now() + timedelta(
        minutes=settings.OTP_EXPIRE_MINUTES
    )
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @validator("user_id", pre=True)
    def validate_full_name(cls, v: Union[str, TimeStampedModel]) -> str:
        # extract user uuid from user object pre validation
        from app.models import User

        if isinstance(v, User):
            v = v.uuid
        return v


class OTPRead(OTPBase, TimeStampedModel):
    uuid: str
    user_id: str
    code: str
    created_at: datetime
    expires_at: datetime
