from typing import Any, List

from db.session import engine
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi_pagination import paginate
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from sqlmodel import select

from app import models
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/", response_model=JsonApiPage[models.UserRead])
def read_users(
    db: Session = Depends(deps.get_db),
    offset: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieves a list of users
    """
    with Session(engine) as session:
        users = session.exec(select(models.User).offset(offset).limit(limit)).all()
        return paginate(users)


@router.put("/me", response_model=models.UserRead)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user: models.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    with Session(engine) as session:
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = user.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(current_user, key, value)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return current_user


@router.get("/me", response_model=models.UserRead)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/sign-up", response_model=models.UserRead)
def sign_up(
    *,
    db: Session = Depends(deps.get_db),
    user_in: models.UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    try:
        with Session(engine) as session:
            user = models.User.from_orm(user_in)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.get("/{user_id}", response_model=models.UserRead)
def read_user_by_id(
    user_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id
    """
    with Session(engine) as session:
        statement = select(models.User).where(models.User.uuid == user_id).first()
        user = session.exec(statement)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


@router.put("/{user_id}", response_model=models.UserRead)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    user_in: models.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user
    """
    with Session(engine) as session:
        # user = session.get(models.User, user_id)
        user = session.exec(select(models.User)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = user.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user, key, value)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
