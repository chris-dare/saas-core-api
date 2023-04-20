from typing import List, Optional, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase


class BillManager(CRUDBase[models.Bill, models.BillCreate, models.BillUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: models.BillCreate, user: models.User, organization: models.Organization = None, product: models.Event = None,
    ) -> models.Bill:
        from app import crud
        if not product:
            product = crud.event.get(db=db, uuid=obj_in.product_id)
        organization = crud.organization.get(db=db, uuid=product.organization_id)
        obj_in_data = jsonable_encoder(obj_in)

        # calculate total amount
        total_amount = product.amount * obj_in.quantity

        db_obj = self.model(**obj_in_data,
            customer_id=user.uuid,
            customer_name=user.full_name,
            customer_email=user.email,
            customer_mobile=user.mobile,
            organization_name=organization.name,
            organization_id=organization.uuid,
            service_or_product_name=product.title,
            unit_price=product.amount,
            total_amount=total_amount,
            charge=total_amount
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


    def get_multi_by_owner(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100,
    ) -> List[models.Bill]:
        return (
            db.query(self.model)
            .filter(
                models.Bill.customer_id == user_id,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def remove(self, db: Session, *, uuid: Optional[Any]) -> models.Bill:
        """Cancels a bill"""
        db_obj: models.Bill = db.query(self.model).get(uuid=uuid)
        db_object, action_history = db_obj.cancel()
        # TODO save action history when implemented
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


bill = BillManager(models.Bill)
