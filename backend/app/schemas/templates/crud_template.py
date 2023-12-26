import datetime
import uuid as uuid_pkg
from typing import List, Optional

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.utils import ModeOfMessageDelivery
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .crud_base import CRUDBase


class CRUDTemplate(
    CRUDBase[models.Organization, models.OrganizationCreate, models.OrganizationRead]
):
    async def create(
        self, db: AsyncSession, *, obj_in: models.OrganizationCreate
    ) -> models.Organization:
        raise NotImplementedError

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: models.Organization,
        obj_in: models.OrganizationUpdate
    ) -> models.Organization:
        raise NotImplementedError

    async def remove(
        self,
        db: AsyncSession,
        *,
        uuid: Optional[uuid_pkg.UUID],
        obj: models.Organization = None,
        soft_delete: bool = True
    ) -> models.Organization:
        raise NotImplementedError
