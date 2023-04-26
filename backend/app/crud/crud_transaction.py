from typing import List, Optional, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase

import httpx


class TransactionManager(CRUDBase[models.Transaction, models.TransactionCreate, models.TransactionUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: models.TransactionCreate, user: models.User, bill: models.Bill,
    ) -> models.Transaction:
        """Creates a transaction for a given customer.
        Initializes a payment transaction with a 3rd party payment gateway"""
        from app import crud
        # confirm that user is the same customer of the bill
        if user.uuid != bill.customer_id:
            raise ValueError("Something went wrong whilst we were setting up your transaction. \
                Please try again later or contact our support team.")
        obj_in_data = jsonable_encoder(obj_in)
        customer_email = user.email
        db_obj: models.Transaction = self.model(**obj_in_data,
            customer_id=user.uuid,
            customer_name=user.full_name,
            customer_email=customer_email,
            customer_mobile=user.mobile,
            service_or_product_name=bill.service_or_product_name,
            amount=bill.charge,
            product_id=bill.product_id,
            currency=bill.currency,
        )
        db_obj.initialize()
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self, db: AsyncSession, id: Optional[Any] = None, uuid: Optional[Any] = None,
        customer_id: Optional[str] = None,
    ) -> Optional[models.Transaction]:
        statement = select(
            self.model
        ).where(
            self.model.uuid == uuid,
        )
        if customer_id:
            statement = statement.where(models.Transaction.customer_id == customer_id)
        obj = await db.execute(statement=statement)
        return obj.scalar_one_or_none()

    async def get_multi_by_owner(
        self, db: AsyncSession, *, customer_id: Optional[str] = None, organization_id: Optional[str] = None, skip: int = 0, limit: int = 100,
    ) -> List[models.Bill]:
        """Get all Transactions attributed to a customer or a vendor
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
        List[models.Transaction]
            A list of Transactions belonging to the customer or vendor
        """
        statement = select(
            models.Transaction
        )
        if not organization_id and not customer_id:
            raise ValueError("Technical error: User or organization id required!")
        if organization_id:
            statement = statement.where(models.Transaction.organization_id == organization_id)
        elif customer_id:
            statement = statement.where(models.Transaction.customer_id == customer_id)
        statement = statement.offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()  # type: Transaction | None

    async def cancel(self, db: AsyncSession, *, uuid: Optional[Any]) -> models.Transaction:
        """Cancels a transaction"""
        db_obj: models.Transaction = await self.get(db, uuid=uuid)
        db_object, action_history = db_obj.cancel()
        # TODO save action history when implemented
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


transaction = TransactionManager(models.Transaction)
