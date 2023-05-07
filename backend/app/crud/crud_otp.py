import datetime
from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.security import generate_otp_code
from app.core.config import settings
from app.crud.base import CRUDBase
from app.utils import ModeOfMessageDelivery, send_sms


class CRUDOtp(CRUDBase[models.OTP, models.OTPCreate, models.OTPRead]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: models.OTPCreate = None, user: models.User,
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
        if mode == ModeOfMessageDelivery.EMAIL:
            subject = f"Your OTP verification code is {otp.code}"
        elif mode == ModeOfMessageDelivery.SMS:
            message = f"Your OTP verification code is {otp.code}"
        client_response = await crud.user.notify(
            user=user, message=message, subject=subject,
            mode=mode, template=settings.EMAIL_OTP_TEMPLATE_ID,
            template_vars={"first_name": user.first_name, "otp_code": otp.code},
        )
        return client_response

otp = CRUDOtp(models.OTP)
