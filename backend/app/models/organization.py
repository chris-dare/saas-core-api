"""The :mod:`app.models.organization` module contains a ORMs used to persist and retrieve
data concerning organizations on HyperSenta
"""
# Author: Christopher Dare

import uuid as uuid_pkg
from datetime import datetime
from typing import Any, Dict, Optional

import sqlalchemy as sa
from app.schemas import (
    OperatingCountryResourceSchema,
    OperatingCountryType,
    OrganizationType,
    OrganizationVerificationType,
)
from pydantic import EmailStr, validator
from sqlmodel import ARRAY, Column, Field, SQLModel, String

from .abstract import TimeStampedModel


class OrganizationBase(SQLModel, OperatingCountryResourceSchema):
    name: str = Field(
        description="Business name", unique=True, index=True, nullable=False
    )


class Organization(OrganizationBase, TimeStampedModel, table=True):
    pk: Optional[int] = Field(
        sa_column=Column(
            "pk",
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
    country: str = Field(description="Country of address")
    email: Optional[EmailStr] = Field(
        description="Owner's email address", index=True, nullable=True
    )
    is_deleted: bool = Field(
        description="Flag to mark business's active status", default=False
    )
    is_verified: bool = Field(
        description="Flag to mark business's verification status", default=False
    )
    line_address: Optional[str] = Field(
        description="Business Line address", nullable=False
    )
    organization_type: OrganizationType = Field(description="Type of organization")
    owner_first_name: str = Field(description="Owner's first name", nullable=False)
    owner_last_name: str = Field(description="Owner's last name", nullable=False)
    region: str = Field(description="Region of address")
    verification_id: str = Field(description="ID of verification record", nullable=True)
    verification_document: str = Field(
        description="Name of uploaded document used to verify the organization",
        nullable=True,
    )
    verification_mode_types: list[OrganizationVerificationType] = Field(
        description="Methods used to verify the organization",
        nullable=True,
        sa_column=Column(ARRAY(String)),
    )
    name: str = Field(
        description="Business name", unique=True, index=True, nullable=False
    )
    created_by_id: uuid_pkg.UUID = Field(
        foreign_key="users.uuid",
        index=True,
        nullable=False,
        description="User who created the organization",
    )
    created_by_name: str = Field(
        description="Name of user who created the organization", nullable=False
    )

    # meta properties
    __tablename__ = "organizations"
    # Ensure case-insensitive uniqueness for the 'name' column
    # __table_args__ = (
    #     sa.UniqueConstraint(sa.func.lower("name"), name="unique_name_case_insensitive"),
    # )


class OrganizationCreate(OrganizationBase):
    country: OperatingCountryType = Field(
        description="Country of the indicated line address",
    )
    email: str = Field(description="Email address of organization (or its owner)")
    line_address: Optional[str] = Field(
        default="", description="Line address of organization"
    )
    organization_type: OrganizationType = Field(description="Type of organization")
    owner_id: uuid_pkg.UUID = Field(description="User id of the organization's owner")
    region: str = Field(
        default="",
        description="Region of the indicated line address",
    )


class OrganizationRead(OrganizationBase):
    country: str
    email: str
    line_address: str
    organization_type: OrganizationType
    owner_first_name: str
    owner_last_name: str
    region: str
    verification_document: Optional[str] = Field(
        description="Link to uploaded verification document"
    )


class OrganizationUpdate(OrganizationBase):
    country: Optional[str] = None
    email: Optional[str] = None
    line_address: Optional[str] = None
    name: Optional[str] = None
    region: Optional[str] = None
    updated_at: datetime = datetime.now()
