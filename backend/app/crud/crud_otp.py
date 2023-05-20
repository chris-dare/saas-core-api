import datetime
from typing import List, Optional

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
        """
        Create an OTP for a user. Returns existing OTP if it is unused and has not expired
        """
        # check if there is an existing otp for the user valid until 5 minutes from now
        db_obj = await self.get_user_otp(
            db=db, user=user, token_type=obj_in.token_type,
            valid_util = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
        )
        if db_obj:
            return db_obj
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user.uuid, code=generate_otp_code())
        if obj_in.token_type == models.OTPTypeChoice.PASSWORD_RESET:
            # change the otp code to a unique uuid before persisting to db
            db_obj.code = str(db_obj.uuid) # use the existing uuid which has a unique constraint
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_user_otp(self,
        db: AsyncSession, *,
        user: models.User,
        token_type: models.OTPTypeChoice,
        code: Optional[str] = None,
        valid_util: datetime.datetime = datetime.datetime.now(datetime.timezone.utc),
    ) -> models.OTP:
        otp = await self.get(
            db=db, user_id=user.uuid, token_type=token_type, code = code, valid_util=valid_util
        )
        return otp

    async def get(
        self, *,
        db: AsyncSession,
        uuid: Optional[str] = None,
        code: Optional[str] = None,
        token_type: models.OTPTypeChoice,
        user_id: Optional[str] = None,
        valid_util: datetime.datetime = datetime.datetime.now(datetime.timezone.utc),
    ) -> Optional[models.OTP]:
        """
        Get an OTP by its uuid and user_id
        """
        if not (uuid or user_id):
            raise ValueError("Technical error: Invalid arguments (user id or obj uuid required)")
        if not isinstance(token_type, models.OTPTypeChoice):
            raise ValueError("Technical error: Invalid token type argument")
        statement = select(models.OTP).where(
            models.OTP.token_type == token_type.value, models.OTP.is_used.is_(False),
            models.OTP.expires_at > valid_util,
        )
        if user_id:
            statement = statement.where(models.OTP.user_id == user_id)
        if uuid:
            statement = statement.where(models.OTP.uuid == uuid)
        if code:
            statement = statement.where(models.OTP.code == code)
        statement = statement.order_by(models.OTP.created_at.desc())
        results = await db.execute(statement=statement)
        obj: [models.OTP, None] = results.scalars().first()
        # TODO: check if the otp has expired
        # if obj and obj.expires_at < datetime.datetime.now(datetime.timezone.utc):
        #     obj = None
        return obj

    async def get_multi_by_owner(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[models.OTP]:
        results = await db.execute(
            select(models.OTP).where(models.OTP.user_id == user_id).order_by(models.OTP.created_at.desc())
        )
        return results.scalars().all()

    async def send_otp(self,
        db: AsyncSession, *,
        user: models.User,
        mode: ModeOfMessageDelivery == ModeOfMessageDelivery.SMS,
        message: str = None,
        otp: models.OTP,
        token_type: models.OTPTypeChoice,
    ) -> bool:
        from app import crud
        if not otp:
            otp: models.OTP = await self.get_user_otp(db=db, user=user, token_type=token_type)
        if mode == ModeOfMessageDelivery.EMAIL:
            subject = f"Your OTP verification code is {otp.code}"
        elif mode == ModeOfMessageDelivery.SMS:
            message = f"Your OTP verification code is {otp.code}"
        template = settings.EMAIL_OTP_TEMPLATE_ID # default generic template
        template_vars={"first_name": user.first_name, "otp_code": otp.code} # default template vars
        if token_type == models.OTPTypeChoice.PASSWORD_RESET:
            subject = "Reset your password"
            template = settings.PASSWORD_RESET_TEMPLATE_ID
            template_vars={
                "first_name": user.first_name,
                "password_reset_url": f"{settings.CLIENT_APP_HOST}/reset-password?token={otp.code}"
            }
        client_response = await crud.user.notify(
            user=user, message=message, subject=subject,
            mode=mode, template=template,
            template_vars=template_vars,
        )
        return client_response

    async def mark_as_used(self, db: AsyncSession, *, otp: models.OTP) -> models.OTP:
        """
        Mark an OTP as used
        """
        otp.is_used = True
        otp.used_at = datetime.datetime.now()
        db.add(otp)
        await db.commit()
        await db.refresh(otp)
        return otp

otp = CRUDOtp(models.OTP)
