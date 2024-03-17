"""The :mod:`app.models.template` module contains a ORMs used to persist and retrieve
data concerning templates on HyperSenta
"""
# Author: Christopher Dare

import uuid as uuid_pkg
from datetime import datetime
from typing import Any, Dict, Optional

import sqlalchemy as sa
from app.schemas import TemplateType, TemplateVerificationType
from pydantic import EmailStr, validator
from sqlmodel import ARRAY, Column, Field, SQLModel, String

from .abstract import TimeStampedModel


class TemplateBase(SQLModel):
    name: str = Field(
        description="Business name", unique=True, index=True, nullable=False
    )


class Template(TemplateBase, TimeStampedModel, table=False):
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
        description="User who owns the template",
    )

    # meta properties
    __tablename__ = "templates"


class TemplateCreate(TemplateBase):
    name: str = None


class TemplateRead(TemplateBase):
    name: Optional[str] = None


class TemplateUpdate(TemplateBase):
    name: Optional[str] = None
    updated_at: datetime = datetime.now()
