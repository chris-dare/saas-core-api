from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase


class OrganizationManager(CRUDBase[models.Organization, models.OrganizationCreate, models.OrganizationUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: models.OrganizationCreate, user: models.User, commit=True,
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
            db.commit()
            # TODO: Add owner as member of newly created organization
            db.refresh(db_obj)
        return db_obj


    def get_multi_by_owner(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[models.Organization]:
        return (
            db.query(self.model)
            .filter(models.Organization.owner_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


organization = OrganizationManager(models.Organization)
