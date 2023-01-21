from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase


class CourseManager(CRUDBase[models.Course, models.CourseCreate, models.CourseUpdate]):
    def create_with_owner(
        self, db: Session, *, obj_in: models.CourseCreate, user: models.User, organization: models.Organization
    ) -> models.Course:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data,
            user_id=user.uuid,
            instructor_name=user.full_name,
            organization_name=organization.name,
            organization_id=organization.uuid,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


    def get_multi_by_owner(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100, organization_id: str = None,
    ) -> List[models.Course]:
        return (
            db.query(self.model)
            .filter(
                models.Course.user_id == user_id,
                models.Course.organization_id == organization_id,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


course = CourseManager(models.Course)
