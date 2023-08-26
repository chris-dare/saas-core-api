import datetime
from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import CRUDBase
from app.django_emr.models import User
from app.django_emr.utils import verify_user_pbkdf2_sha256_password


class CRUDUser(CRUDBase[User, User, User]):
    async def get_by_email_or_mobile(
        self, db: AsyncSession, *, email: EmailStr, mobile: str = None
    ) -> Optional[User]:
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

    async def get_by_uuid(self, db: AsyncSession, *, uuid: str) -> Optional[User]:
        statement = select(User).where(User.uuid == uuid)
        results = await db.execute(statement)
        return results.scalar_one_or_none()

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_email_or_mobile(db, email=email, mobile=None)
        if not user:
            return None
        if not verify_user_pbkdf2_sha256_password(
            plain_password=password, hashed_password=user.password
        ):
            return None
        # set the last login date of the user
        user.last_login = datetime.datetime.utcnow()
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active


user = CRUDUser(User)
