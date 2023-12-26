import datetime
import uuid as uuid_pkg
from typing import List, Optional

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.utils import ModeOfMessageDelivery
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .crud_base import CRUDBase


class CRUDOrganization(
    CRUDBase[models.Organization, models.OrganizationCreate, models.OrganizationRead]
):
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: models.OrganizationCreate,
        current_user: models.User,
    ) -> models.Organization:
        from app import crud

        if current_user.uuid != obj_in.owner_id and not current_user.is_superuser:
            raise ValueError("Not enough permissions!")
        # find all organizations with existing name or owned by the obj_in.owner_id
        statement = select(models.Organization).where(
            or_(
                models.Organization.name == obj_in.name,
                models.Organization.owner_id == obj_in.owner_id,
            )
        )
        results = await db.execute(statement)
        records = results.scalars().all()
        error_messages = []
        for i in records:
            if i.name == obj_in.name:
                error_messages.append(
                    f"An organization named {obj_in.name} already exists"
                )
            if i.owner_id == obj_in.owner_id:
                error_messages.append(
                    f"User has already created {len(records)} organizations"
                    + " (Maximum allowed is 1)"
                )
        if error_messages:
            raise ValueError(", ".join(error_messages))

        owner = (
            current_user
            if current_user.uuid == obj_in.owner_id
            else await crud.user.get_by_uuid(obj_in.owner_id)
        )
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = models.Organization(
            **obj_in_data,
            owner_first_name=owner.first_name,
            owner_last_name=owner.last_name,
            created_by_id=current_user.uuid,
            created_by_name=current_user.full_name,
        )
        db.add(db_obj)
        # TODO: Add owner as member of newly created organization
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: models.Organization,
        obj_in: models.OrganizationUpdate,
    ) -> models.Organization:
        raise NotImplementedError

    async def remove(
        self,
        db: AsyncSession,
        *,
        uuid: Optional[uuid_pkg.UUID],
        obj: models.Organization = None,
        soft_delete: bool = True,
    ) -> models.Organization:
        raise NotImplementedError


organization = CRUDOrganization(models.Organization)
