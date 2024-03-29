"""The :mod:`app.models.abstract` module contains abstract classes for building persistent models
data concerning organizations on Serenity
"""
# Author: Christopher Dare

import uuid as uuid_pkg
from datetime import datetime

from sqlmodel import Column, DateTime, Field, SQLModel


class TimeStampedModel(SQLModel):
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        unique=True,
        index=True,
        nullable=False,
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=datetime.utcnow, default=datetime.utcnow
        )
    )
