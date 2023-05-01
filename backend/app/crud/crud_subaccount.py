from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.config import settings
from app.crud.base import CRUDBase


class SubAccountManager(CRUDBase[models.SubAccount, models.SubAccountCreate, models.SubAccountUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: models.SubAccountCreate, user: models.User
    ) -> models.SubAccount:
        obj_in_data = jsonable_encoder(obj_in)
        #TODO: Create subaccount with payment service provider before saving in app db
        db_obj = self.model(**obj_in_data,
            owner_id=user.uuid,
            organization_name=user.last_used_organization_name,
            organization_id=user.last_used_organization_id,
            percentage_charge=settings.DEFAULT_TRANSACTION_FEE,
            is_primary=False,
            is_deleted=False,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


    async def get_multi_by_owner(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100, organization_id: str = None,
    ) -> List[models.SubAccount]:
        statement = select(
            models.SubAccount
        ).where(
            models.SubAccount.owner_id == user_id,
        )
        if organization_id:
            statement = statement.where(
                models.SubAccount.organization_id == organization_id,
            )
        obj = await db.execute(statement=statement)
        return obj.scalars().all()


subaccount = SubAccountManager(models.SubAccount)
