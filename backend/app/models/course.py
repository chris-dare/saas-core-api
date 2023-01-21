"""The :mod:`app.models.course` module contains a ORMs used to persist and retrieve
data concerning online course on HyperSenta

A course typically has the following information:
1. Name
2. Summary and full description
3. Instructor(s)
4. Course length in hours and minutes
5. Number of videos/sessions in course
5. Category
6. Type (online, pre-recorded or hybrid)
7. Learning plan
"""
# Author: Christopher Dare

from datetime import datetime
import uuid as uuid_pkg
import orm
import sqlalchemy as sa
from pydantic import EmailStr, validator
from sqlmodel import Column, Field, SQLModel, UniqueConstraint

from decimal import Decimal
from enum import Enum, IntEnum

from app.config.api_config import api_settings
from app.utils.parser import parse_mobile_number

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


class CourseBase(SQLModel):
    course_name: str = Field(
        description="Name of course", nullable=False
    )
    description: str = Field(
        description="Detailed description of course", nullable=False, default="",
    )
    summary: str = Field(
        description="One sentence description of the course (the value proposition).", nullable=False, default=""
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


class Course(CourseBase, TimeStampedModel, table=True):
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
        description="Course instructor",
    )
    organization_name: str = Field(
        description="Business name", unique=False, index=True, nullable=False
    )
    organization_id: uuid_pkg.UUID = Field(
        foreign_key="organizations.uuid",
        index=True,
        nullable=False,
        description="User who owns the Course",
    )

    __table_args__ = (
        UniqueConstraint('course_name', 'organization_id', name='_organization_course_name'),
    )

    # meta properties
    __tablename__ = "courses"


class CourseCreate(CourseBase):
    course_name: str
    description: Optional[str] = ""
    summary: str
    mode_of_delivery: Optional[ModeOfDelivery] = ModeOfDelivery.ONLINE
    category: Optional[str] = None
    application_deadline: datetime = datetime.now()
    start_date: datetime = datetime.now()
    end_date: datetime = datetime.now()


class CourseRead(CourseBase):
    uuid: uuid_pkg.UUID
    organization_id: uuid_pkg.UUID
    user_id: uuid_pkg.UUID
    instructor_name: str
    organization_name: str
    keywords: Optional[Any] = None


class CourseUpdate(CourseBase):
    course_name: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    mode_of_delivery: Optional[ModeOfDelivery] = None
    category: Optional[str] = None
    application_deadline: Optional[datetime] = datetime.now()
    start_date: Optional[datetime] = datetime.now()
    end_date: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
