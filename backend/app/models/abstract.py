"""The :mod:`app.models.abstract` module contains abstract classes for building persistent models
data concerning organizations on HyperSenta
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
        description="External UUID",
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow),
        description="Date and time the object was created",
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), onupdate=datetime.utcnow, default=datetime.utcnow
        ),
        description="Last date and time the object was updated",
    )
