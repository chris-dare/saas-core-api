"""The :mod:`app.models.organizationMember` module contains a ORMs used to persist and retrieve 
data concerning organizationMembers on HyperSenta
"""
# Author: Christopher Dare

from datetime import datetime
import uuid as uuid_pkg
import orm
import sqlalchemy as sa
from pydantic import EmailStr, validator
from sqlmodel import Column, Field, SQLModel, UniqueConstraint

from enum import Enum, IntEnum

from app.config.api_config import api_settings

from .abstract import TimeStampedModel
from typing import Optional, Dict, Any


class MemberRole(str, Enum):
    admin = 'admin'
    owner = 'owner'
    billing = 'billing'
    member = 'member'


class OrganizationMemberBase(SQLModel):
    organization_name: str = Field(
        description="Business name", unique=True, index=True, nullable=False
    )
    member_name: str = Field(
        description="Team member name", unique=True, index=True, nullable=False
    )
    email: str
    is_active: bool = True
    role: MemberRole = MemberRole.member


class OrganizationMember(OrganizationMemberBase, TimeStampedModel, table=True):
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
    user_id: uuid_pkg.UUID = Field(
        foreign_key="users.uuid",
        unique=True,
        index=True,
        nullable=False,
        description="User who owns the organizationMember",
    )
    organization_id: uuid_pkg.UUID = Field(
        foreign_key="organizations.uuid",
        unique=True,
        index=True,
        nullable=False,
        description="User who owns the organizationMember",
    )
    organization_name: str = Field(description="Orgnanization", nullable=False)
    member_name: str = Field(description="Member", nullable=False)
    email: EmailStr = Field(
        description="Member's email address", index=True, nullable=False
    )
    is_active: bool = Field(
        description="Flag to mark business's active status", default=False
    )
    role: MemberRole = Field(description="Role of member in organization", default=MemberRole.member, nullable=False)

    __table_args__ = (
        UniqueConstraint('email', 'organization_id', name='_organization_member_email'),
        UniqueConstraint('user_id', 'organization_id', name='_organization_member_user'),
    )

    # meta properties
    __tablename__ = "organization_members"


class OrganizationMemberCreate(OrganizationMemberBase):
    email: str


class OrganizationMemberRead(OrganizationMember):
    pass


class OrganizationMemberUpdate(OrganizationMemberBase):
    member_name: Optional[str] = None
    organization_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[MemberRole] = None
    updated_at: datetime = datetime.now()
