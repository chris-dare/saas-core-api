import datetime
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.crud.base import CRUDBase
from app import models
from app.models.user import User, UserCreate, UserUpdate
from app.utils.security import check_password, make_password
from app.utils.messaging import ModeOfMessageDelivery, send_sms, send_email


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_mobile(self, db: Session, *, mobile: str) -> Optional[User]:
        return db.query(User).filter(User.mobile == mobile).first()

    def get_by_uuid(self, db: Session, *, uuid: str) -> Optional[User]:
        return db.query(User).filter(User.uuid == uuid).first()

    def create(self, db: Session, *, obj_in: UserCreate, notify: bool = True, is_superuser = False,) -> User:
        new_user: User = User(
            **obj_in.dict(),
            hashed_password=get_password_hash(obj_in.password),
            is_superuser=is_superuser,
        )
        db.add(new_user)
        db.commit()
        # create a new organization for the user
        organization = self.create_organization(
            db=db,
            organization_name=obj_in.email,
            owner=new_user,
            commit=True,
        )

        # set the user's last used organization so it can be retrieved by the client app
        db.refresh(new_user)
        if notify:
            self.notify(
                user=new_user,
                subject="welcome to {settings.PROJECT_NAME}",
            message=f"Hi {new_user.full_name}, welcome to {settings.PROJECT_NAME}")
        return new_user

    def create_organization(self, db: Session, organization_name: str, owner: User, commit: bool = True):
        from app.crud.crud_organization import organization as organization_manager
        organization_create = models.OrganizationCreate(
            name=organization_name,
            mobile=owner.mobile,
            email=owner.email,
        )
        return organization_manager.create_with_owner(
            db=db,
            obj_in=organization_create,
            user=owner,
            commit=commit,
        )

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
