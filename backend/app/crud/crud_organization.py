from typing import List, Optional, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase


class OrganizationManager(CRUDBase[models.Organization, models.OrganizationCreate, models.OrganizationUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: models.OrganizationCreate, user: models.User, commit=True,
    ) -> models.Organization:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data,
            owner_id=user.uuid,
            owner_first_name=user.first_name,
            owner_last_name=user.last_name,
        )
        if commit:
            db.add(db_obj)
            user.last_used_organization_id = db_obj.uuid
            user.last_used_organization_name = db_obj.name
            db.add(user)
            await db.commit()
            # TODO: Add owner as member of newly created organization
            await db.refresh(db_obj)
        return db_obj

    async def get(
            self, db: AsyncSession, uuid: Optional[Any] = None,
            owner_id: Optional[str] = None, name: Optional[str] = None,
    ) -> Optional[models.Organization]:
        statement = select(
            models.Organization
        ).where(
            models.Organization.uuid == uuid,
        )
        if owner_id:
            statement = statement.where(
                models.Organization.owner_id == owner_id,
            )
        if name:
            statement = statement.where(
                models.Organization.name == name,
            )
        obj = await db.execute(statement=statement)
        return obj.scalar_one_or_none()

    async def get_multi_by_owner(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[models.Organization]:
        results = await db.execute(
            select(models.Organization).where(models.Organization.owner_id == user_id).order_by(models.Organization.created_at.desc())
        )
        return results.scalars().all()

organization = OrganizationManager(models.Organization)
