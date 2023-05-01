"""The :mod:`app.models.event` module contains a ORMs used to persist and retrieve
data concerning online event on HyperSenta

A event typically has the following information:
1. Name
2. Summary and full description
3. Instructor(s)
4. Duration in hours and minutes
5. Number of videos/sessions in event
5. Category
6. Type (online, pre-recorded or hybrid)
7. Learning plan
"""
# Author: Christopher Dare

from datetime import datetime
import uuid as uuid_pkg
import orm
import sqlalchemy as sa
from sqlmodel import Column, Field, SQLModel, UniqueConstraint

from decimal import Decimal
from enum import Enum

from app.config.api_config import api_settings

from .abstract import TimeStampedModel
from typing import Optional, Dict, Any


class ModeOfDelivery(str, Enum):
    ONLINE = 'online'
    PRE_RECORDED = 'pre-recorded'
    HYBRID = 'hybrid'


class CurrencyType(str, Enum):
    GHS = "GHS"
    USD = "USD"


class SubscriptionType(str, Enum):
    ONE_TIME = "one-time"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class EventBase(SQLModel):
    title: str = Field(
        description="Name of event", nullable=False
    )
    description: str = Field(
        description="Detailed description of event", nullable=False, default="",
    )
    summary: str = Field(
        description="One sentence description of the event (the value proposition).", nullable=False, default=""
    )
    currency: Optional[CurrencyType] = CurrencyType.USD
    amount: Optional[Decimal] = 0
    subscription_type: Optional[SubscriptionType] = SubscriptionType.ONE_TIME
    subscription_months: Optional[int] = 0
    mode_of_delivery: Optional[ModeOfDelivery] = ModeOfDelivery.ONLINE
    category: Optional[str] = None
    keywords: Optional[str] = None
    is_active: bool = True
    application_deadline: datetime
    start_date: datetime
    end_date: datetime


class Event(EventBase, TimeStampedModel, table=True):
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
    instructor_name: str = Field(
        description="Instructor name", unique=False, index=True, nullable=False
    )
    user_id: uuid_pkg.UUID = Field(
        foreign_key="users.uuid",
        index=True,
        nullable=False,
        description="Event instructor",
    )
    organization_name: str = Field(
        description="Business name", unique=False, index=True, nullable=False
    )
    organization_id: uuid_pkg.UUID = Field(
        foreign_key="organizations.uuid",
        index=True,
        nullable=False,
        description="User who owns the Event",
    )

    __table_args__ = (
        UniqueConstraint('title', 'organization_id', name='_organization_title'),
    )

    # meta properties
    __tablename__ = "events"


class EventCreate(EventBase):
    title: str
    description: Optional[str] = ""
    summary: str
    mode_of_delivery: Optional[ModeOfDelivery] = ModeOfDelivery.ONLINE
    category: Optional[str] = None
    application_deadline: datetime = datetime.now()
    start_date: datetime = datetime.now()
    organization_id: uuid_pkg.UUID = Field(description="Organization ID")
    end_date: datetime = datetime.now()


class EventRead(EventBase):
    uuid: uuid_pkg.UUID
    organization_id: uuid_pkg.UUID
    user_id: uuid_pkg.UUID
    instructor_name: str
    organization_name: str
    keywords: Optional[Any] = None


class EventUpdate(EventBase):
    title: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    mode_of_delivery: Optional[ModeOfDelivery] = None
    category: Optional[str] = None
    application_deadline: Optional[datetime] = datetime.now()
    start_date: Optional[datetime] = datetime.now()
    end_date: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
