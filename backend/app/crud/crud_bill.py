from typing import List, Optional, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase


class BillManager(CRUDBase[models.Bill, models.BillCreate, models.BillUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: models.BillCreate, user: models.User, organization: models.Organization = None, product: models.Event = None,
    ) -> models.Bill:
        from app import crud
        if not product:
            product = await crud.event.get(db=db, uuid=obj_in.product_id)
        obj_in_data = jsonable_encoder(obj_in)

        # calculate total amount
        total_amount = product.amount * obj_in.quantity

        db_obj = self.model(**obj_in_data,
            customer_id=user.uuid,
            customer_name=user.full_name,
            customer_email=user.email,
            customer_mobile=user.mobile,
            organization_name=product.organization_name,
            organization_id=product.organization_id,
            service_or_product_name=product.title,
            unit_price=product.amount,
            total_amount=total_amount,
            charge=total_amount
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


    async def get(
        self, db: AsyncSession, id: Optional[Any] = None, uuid: Optional[Any] = None,
        customer_id: str = None, organization_id: str = None
    ) -> Optional[models.Bill]:
        statement = select(
            self.model
        ).where(
            self.model.uuid == uuid,
        )
        if customer_id:
            statement = statement.where(models.Bill.customer_id == customer_id)
        if organization_id:
            statement = statement.where(models.Bill.organization_id == organization_id)
        obj = await db.execute(statement=statement)
        return obj.scalar_one_or_none()

    async def get_multi_by_owner(
        self, db: AsyncSession, *, customer_id: Optional[str] = None, organization_id: Optional[str] = None, skip: int = 0, limit: int = 100,
    ) -> List[models.Bill]:
        """Get all bills attributed to a customer or a vendor
        Parameters:
        -----------
        db: AsyncSession
            The database session
        user_id: str
            The user id
        organization_id: str
            The organization id
        skip: int
            The number of records to skip
        limit: int
            The number of records to return
        Returns:
        --------
        List[models.Bill]
            A list of bills belonging to the customer or vendor
        """
        statement = select(
            models.Bill
        )
        if not organization_id and not customer_id:
            raise ValueError("Technical error: User or organization id required!")
        if organization_id:
            statement = statement.where(models.Bill.organization_id == organization_id)
        elif customer_id:
            statement = statement.where(models.Bill.customer_id == customer_id)
        statement = statement.offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()  # type: Bill | None

    async def cancel(self, db: AsyncSession, *, uuid: Optional[Any]) -> models.Bill:
        """Cancels a bill"""
        db_obj: models.Bill = db.query(self.model).get(uuid=uuid)
        db_object, action_history = db_obj.cancel()
        # TODO save action history when implemented
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


bill = BillManager(models.Bill)
