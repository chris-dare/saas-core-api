from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.security import generate_otp_code
from app.crud.base import CRUDBase
from app.utils import ModeOfMessageDelivery, send_sms, send_email


class CRUDOtp(CRUDBase[models.OTP, models.OTPCreate, models.OTPRead]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: models.OTPCreate, user: models.User
    ) -> models.OTP:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, code=generate_otp_code())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_user_otp(self, db: AsyncSession, *, user: models.User) -> models.OTP:
        user_otp = await db.execute(
            select(models.OTP).where(models.OTP.user_id == user.uuid).order_by(models.OTP.created_at.desc())
        )
        return user_otp.scalars().first()

    async def get_multi_by_owner(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[models.OTP]:
        results = await db.execute(
            select(models.OTP).where(models.OTP.user_id == user_id).order_by(models.OTP.created_at.desc())
        )
        return results.scalars().all()

    async def send_otp(self, db: AsyncSession, *, user: models.User, mode: ModeOfMessageDelivery == ModeOfMessageDelivery.SMS, message: str = None, otp: models.OTP) -> bool:
        from app import crud
        if not otp:
            otp: models.OTP = await self.get_user_otp(db=db, user=user)
        if not message:
            message = f"Your OTP is {otp.code}"
        message_delivery_status = await crud.user.notify(user=user, message=message, subject="Your verification code", mode=mode)
        return message_delivery_status

otp = CRUDOtp(models.OTP)
