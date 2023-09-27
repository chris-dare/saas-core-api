"""The :mod:`app.models.OTP` module contains a ORMs used to persist and retrieve 
data concerning OTPs on HyperSenta
"""
# Author: Christopher Dare

import enum
import uuid as uuid_pkg
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

import phonenumbers
import sqlalchemy as sa
from pydantic import EmailStr, validator, BaseModel
from sqlmodel import Column, DateTime, Field, SQLModel

from data_bridge.core.config import settings

from .abstract import TimeStampedModel


class OTPTypeChoice(str, enum.Enum):
    PASSWORD_RESET = "password_reset"
    USER_VERIFICATION = "user_verification"


class OTPBase(SQLModel):
    token_type: OTPTypeChoice = Field(
        description="Type of OTP code/token",
        default=OTPTypeChoice.USER_VERIFICATION,
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
    user_id: uuid_pkg.UUID = Field(
        description="User's public UUID", nullable=False, index=True
    )
    is_used: bool = Field(
        description="Indicates whether the OTP has already been used", default=False
    )
    code: str = Field(description="OTP code", nullable=False)
    used_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
        ),
        description="Datetime when OTP was used",
    )
    expires_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=True),
        ),
        description="OTP expiry datetime",
        default=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
    )

    # meta properties
    __tablename__ = "otp"


# Properties to receive via API on creation
class OTPCreate(OTPBase):
    token_type: OTPTypeChoice = Field(
        description="Type of OTP to generate",
        default=OTPTypeChoice.USER_VERIFICATION,
    )
    email: Optional[EmailStr] = Field(
        description="User's email address"
    )
    mode: Optional[str] = Field(
        description="Mode of message delivery",
        default="email",
    )


class OTPRead(OTPBase, TimeStampedModel):
    uuid: str
    user_id: str
    code: str
    created_at: datetime
    expires_at: datetime


class PasswordResetOTPPayload(BaseModel):
    new_password: str
    confirm_password: str
    token: str