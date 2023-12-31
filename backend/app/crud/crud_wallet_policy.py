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


class CRUDWalletPolicy(
    CRUDBase[models.WalletPolicy, models.WalletPolicyCreate, models.WalletPolicyRead]
):
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: models.WalletPolicyCreate,
        is_core: bool = False,
        managing_organization: models.Organization,
        commit=True,
    ) -> models.WalletPolicy:
        # check if wallet already exists with the same owner_id, currency and
        # managing_organization_id. If it does, raise an error.
        if managing_organization.uuid != obj_in.managing_organization_id:
            raise ValueError(
                "Technical error: Managing organizations must match."
                + " Contact developer support"
            )
        name_chars = obj_in.name_chars()
        existing_policy = await self.get(
            db=db,
            name_chars=name_chars,
            managing_organization_id=managing_organization.uuid,
        )
        if existing_policy:
            raise ValueError(
                f"A policy with same/similar name {existing_policy.name} already exists"
            )

        obj_in_data: models.WalletPolicyCreate = jsonable_encoder(obj_in)
        db_obj = models.WalletPolicy(
            **obj_in_data,
            is_core=is_core,
            managing_organization_name=managing_organization.name,
            name_chars=name_chars,
            description=obj_in.describe_policy(),
        )
        if not commit:
            return db_obj
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        managing_organization_id: Optional[uuid_pkg.UUID] = None,
    ):
        stmt = select(models.WalletPolicy)
        if managing_organization_id:
            stmt = stmt.where(
                models.WalletPolicy.managing_organization_id
                == managing_organization_id,
            )
        stmt = stmt.offset(skip).limit(limit)
        stmt = stmt.order_by(models.WalletPolicy.name)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get(
        self,
        db: AsyncSession,
        uuid: uuid_pkg.UUID = None,
        managing_organization_id: uuid_pkg.UUID = None,
        name_chars: str = None,
    ) -> Optional[models.Organization]:
        if not uuid and not (managing_organization_id and name_chars):
            type_error_message = (
                "get() missing required positional arguments 'uuid' OR "
                + "('managing_organization_id' and 'name_chars')"
            )
            raise TypeError(type_error_message)
        stmt = select(self.model)

        if uuid:
            stmt.where(
                self.model.uuid == uuid,
            )
        if managing_organization_id:
            stmt = stmt.where(
                self.model.managing_organization_id == managing_organization_id,
            )
        if name_chars:
            stmt = stmt.where(self.model.name_chars == name_chars)
        obj = await db.execute(statement=stmt)
        return obj.scalar_one_or_none()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: models.WalletPolicy,
        obj_in: models.WalletPolicyUpdate,
    ) -> models.WalletPolicy:
        raise NotImplementedError

    async def remove(
        self,
        db: AsyncSession,
        *,
        uuid: Optional[uuid_pkg.UUID],
        obj: models.WalletPolicy = None,
        soft_delete: bool = True,
    ) -> models.WalletPolicy:
        raise NotImplementedError


wallet_policy = CRUDWalletPolicy(model=models.WalletPolicy)
