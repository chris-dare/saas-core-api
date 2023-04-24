from typing import List, Optional, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase


class EventManager(CRUDBase[models.Event, models.EventCreate, models.EventUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: models.EventCreate, user: models.User,
    ) -> models.Event:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data,
            user_id=user.uuid,
            instructor_name=user.full_name,
            organization_name=user.last_used_organization_name,
        )
        db_obj.organization_id = user.last_used_organization_id # Dear self, this simplifies the code written and it's checks, TRUST me
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self, db: AsyncSession, id: Optional[Any] = None, uuid: Optional[Any] = None,
        user_id: str = None, organization_id: str = None,
    ) -> Optional[models.Event]:
        statement = select(
            models.Event
        ).where(
            models.Event.uuid == uuid,
        )
        event = await db.execute(statement=statement)
        if event and user_id and event.user_id != user_id:
            event = None
        if event and organization_id and event.organization_id != organization_id:
            event = None
        return event

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[models.Event]:
        statement = select(
            models.Event
        ).offset(skip).limit(limit)
        events = await db.execute(statement=statement).scalars().all() # type: event | None
        return events if events else []

    async def get_multi_by_owner(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100, organization_id: str = None,
    ) -> List[models.Event]:

        statement = select(
            models.Event
        ).where(
            models.Event.user_id == user_id,
            models.Event.organization_id == organization_id,
        ).offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        events = results.scalars().all()  # type: event | None
        return events if events else []


event = EventManager(models.Event)
