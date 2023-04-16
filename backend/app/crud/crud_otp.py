from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase
from app.utils.messaging import ModeOfMessageDelivery, send_sms, send_email


class CRUDOtp(CRUDBase[models.OTP, models.OTPCreate, models.OTPRead]):
    def create_with_owner(
        self, db: Session, *, obj_in: models.OTPCreate, user: models.User
    ) -> models.OTP:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, code=generate_otp_code())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_user_otp(self, db: Session, *, user: models.User) -> models.OTP:
        return (
            db.query(models.OTP)
            .filter(models.OTP.user_id == user.uuid)
            .order_by(models.OTP.created_at.desc())
            .first()
        )

    def get_multi_by_owner(
        self, db: Session, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[models.OTP]:
        return (
            db.query(self.model)
            .filter(models.OTP.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def send_otp(self, db: Session, *, user: models.User, mode: ModeOfMessageDelivery == ModeOfMessageDelivery.SMS, message: str = None, otp: models.OTP = None,) -> bool:
        from app import crud
        if not otp:
            otp: models.OTP = self.get_user_otp(db=db, user=user)
        if not message:
            message = f"Your OTP is {otp.code}"
        return crud.user.notify(user=user, message=message, subject="Your verification code", mode=mode)


otp = CRUDOtp(models.OTP)
