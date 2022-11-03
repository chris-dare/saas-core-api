from typing import Any, List

from db.session import engine
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import models
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[models.UserRead])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = []
    return users


@router.post("/", response_model=models.UserRead)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: models.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    raise NotImplementedError


@router.put("/me", response_model=models.UserRead)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    raise NotImplementedError


@router.get("/me", response_model=models.UserRead)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=models.UserRead)
def create_user_open(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    raise NotImplementedError


@router.get("/{user_id}", response_model=models.UserRead)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    with Session(engine) as session:
        user = session.get(models.User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


@router.put("/{user_id}", response_model=models.UserRead)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: models.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    raise NotImplementedError
