from typing import List, Optional, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase

import httpx


class TransactionManager(CRUDBase[models.Transaction, models.TransactionCreate, models.TransactionUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: models.TransactionCreate, user: models.User, bill: models.Bill,
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
        db.commit()
        db.refresh(db_obj)
        return db_obj


    def get_multi_by_owner(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100,
    ) -> List[models.Transaction]:
        return (
            db.query(self.model)
            .filter(
                models.Transaction.customer_id == user_id,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def remove(self, db: Session, *, uuid: Optional[Any]) -> models.Transaction:
        """Cancels a transaction"""
        db_obj: models.Transaction = db.query(self.model).get(uuid=uuid)
        db_object, action_history = db_obj.cancel()
        # TODO save action history when implemented
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


transaction = TransactionManager(models.Transaction)
