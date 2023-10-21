import datetime
from typing import Any, Dict, Optional, Union
import uuid as uuid_pkg

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from .crud_base import CRUDBase
from app import models
from app.models.user import User, UserCreate, UserUpdate
from app.utils import check_password, make_password
from app.utils import ModeOfMessageDelivery, send_sms, mailgun_client


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    async def get_by_email_or_mobile(self, db: AsyncSession, *, email: EmailStr, mobile: str = None) -> Optional[User]:
        email = str(email)
        mobile = str(mobile)
        statement = select(User).where((User.email == email) | (User.mobile == mobile))
        existing_user = await db.execute(statement)
        return existing_user.scalar_one_or_none()
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        results = await db.execute(statement)
        return results.scalar_one_or_none()

    async def get_by_mobile(self, db: AsyncSession, *, mobile: str) -> Optional[User]:
        statement = select(User).where(User.mobile == mobile)
        results = await db.execute(statement)
        return results.scalar_one_or_none()

    def get_by_uuid(self, db: Session, *, uuid: str) -> Optional[User]:
        return db.query(User).filter(User.uuid == uuid).first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate, notify: bool = True, is_superuser = False,) -> User:
        existing_user = await self.get_by_email_or_mobile(db=db, email=obj_in.email, mobile=obj_in.mobile)
        if existing_user:
            raise ValueError("Sorry, a user with this email or mobile already exists")
        new_user: User = User(
            **obj_in.dict(),
            uuid=uuid_pkg.uuid4(),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            full_name=f"{obj_in.first_name} {obj_in.last_name}",
            hashed_password=make_password(obj_in.password) if obj_in.password else None,
            is_superuser=is_superuser,
        )
        db.add(new_user)
        await db.commit()

        # set the user's last used organization, so it can be retrieved by the client app
        await db.refresh(new_user)
        if notify:
            # send OTP verification email
            await self.notify(
                user=new_user,
                subject=f"Welcome to {settings.PROJECT_NAME}",
                mode=ModeOfMessageDelivery.EMAIL,
            message=f"Hi {new_user.full_name}, welcome to {settings.PROJECT_NAME}")
        return new_user

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        updated_user = await super().update(db, db_obj=db_obj, obj_in=update_data)
        return updated_user

    async def change_password(self, db: AsyncSession, token: str, new_password: str, confirm_password: str) -> bool:
        """Changes a user's password
        """
        from app import crud
        is_password_changed = False
        if new_password != confirm_password:
            raise ValueError("Passwords do not match")
        otp: models.OTP = await crud.otp.get(db=db, code=token, token_type=models.OTPTypeChoice.PASSWORD_RESET)
        if not otp:
            raise HTTPException(status_code=404, detail="Sorry, you have entered an invalid or expired token")
        user: models.User = await self.get(db=db, uuid=otp.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.password = make_password(new_password)
        await db.commit()
        await db.refresh(user)
        otp = crud.otp.mark_as_used(db=db, otp=otp)
        is_password_changed = True
        return is_password_changed

    async def authenticate(self, db: AsyncSession, *, mobile: str, password: str) -> Optional[User]:
        user = await self.get_by_email_or_mobile(db, mobile=mobile, email=None)
        if not user:
            return None
        if not check_password(hash=user.password, raw_password=password):
            return None
        # set the last login date of the user
        # TODO: this should actually run as a background task
        user.last_login = datetime.datetime.now()
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def activate(self, db: AsyncSession, *, user: User, otp: models.OTP) -> User:
        from app import crud
        if otp.user_id != user.uuid or otp.is_used:
            raise ValueError("Sorry, you have entered an invalid token")
        user.is_active = True
        otp = await crud.otp.mark_as_used(db=db, otp=otp)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def notify(self,
                     user: User,
                     subject: str, mode: ModeOfMessageDelivery = ModeOfMessageDelivery.SMS,
                     message: Optional[str] = None,
                     template: Optional[str] = None, template_vars: dict = None,
                     ) -> bool:
        """Sends user a notification message"""
        client_response = None
        if isinstance(mode, str):
            mode = ModeOfMessageDelivery(mode)
        if mode == ModeOfMessageDelivery.SMS:
            client_response = send_sms(mobile=user.mobile, message=message)
        elif mode == ModeOfMessageDelivery.EMAIL:
            message_delivery_status = False
            response = None
            client_response = mailgun_client.send(
                recipients=[user.email], subject=subject, template=template,
                message=message, template_vars=template_vars
            )
        else:
            raise Exception("Unsupported message delivery mode!")
        return client_response

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)

user = CRUDUser(User)
