import datetime
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import check_password, make_password
from app.utils.messaging import ModeOfMessageDelivery, send_sms


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_uuid(self, db: Session, *, uuid: str) -> Optional[User]:
        return db.query(User).filter(User.uuid == uuid).first()

    def create(self, db: Session, *, obj_in: UserCreate, notify: bool = True) -> User:
        db_obj: User = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        with db_obj as new_user:
            if notify:
                self.notify(db_obj, message=f"Hi {new_user.full_name}, welcome to {settings.PROJECT_NAME}")
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not check_password(hash=user.password, raw_password=password):
            return None
        # set the last login date of the user
        # TODO: this should actually run as a background task
        user.last_login = datetime.datetime.now()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def activate(self, db: Session, *, user: User) -> User:
        user.is_active = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def notify(self, user: User, message: str, subject: str, mode: ModeOfMessageDelivery = ModeOfMessageDelivery.SMS) -> None:
        """Sends user a notification message"""
        if isinstance(mode, str):
            mode = ModeOfMessageDelivery(mode)
        if mode == ModeOfMessageDelivery.SMS:
            send_sms(mobile=user.mobile, message=message)
        elif mode == ModeOfMessageDelivery.EMAIL:
            send_email(recipients=user.email, message=message, subject=subject)
        else:
            raise Exception("Unsupported message delivery mode!")

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
