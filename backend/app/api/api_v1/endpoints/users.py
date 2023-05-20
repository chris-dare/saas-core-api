import datetime
from typing import Any

from db.session import engine
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi_pagination import paginate
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from sqlmodel import select

from app import crud, models, schemas
from app.api import deps
from app.core import security
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
    users = crud.user.get_multi(db=db, limit=limit, skip=offset)
    return paginate(users)


@router.put("/me", response_model=models.UserRead)
async def update_user(
    *,
    db: Session = Depends(deps.get_async_db),
    user_in: models.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update the logged in user
    """
    user = await crud.user.update(db=db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=models.UserRead)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/sign-up", response_model=models.NewUserRead)
async def sign_up(
    *,
    db: Session = Depends(deps.get_async_db),
    user_in: models.UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    try:
        user = await crud.user.create(db=db, obj_in=user_in)
        return models.NewUserRead(
            **user.dict(),
            access_token=security.create_access_token(
                subject=user.uuid, expires_delta=datetime.timedelta(minutes=60) # authenticate the user for 1 hour after sign up
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    return user


@router.post("/activate", response_model=models.UserRead)
async def activate_user(
    email: str = Body(...),
    otp_code: str = Body(...),
    db: Session = Depends(deps.get_async_db),
) -> models.UserRead:
    """
    Activates a newly created user via their OTP
    """
    user = await crud.user.get_by_email_or_mobile(db=db, email=email)
    otp: models.OTP = await crud.otp.get_user_otp(
        db=db,
        user=user,
        code=otp_code,
        token_type=models.OTPTypeChoice.USER_VERIFICATION
    )
    if not otp:
        raise HTTPException(
            status_code=400, detail="We couldn't verify your OTP code. It might be invalid or expired"
        )
    try:
        user = await crud.user.activate(db=db, user=user, otp=otp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    return user


@router.get("/{user_id}", response_model=models.UserRead)
async def read_user_by_id(
    user_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_async_db),
) -> Any:
    """
    Get a specific user by id
    """
    user = await crud.user.get(db=db, uuid=user_id)
    if not event:
        raise HTTPException(status_code=404, detail="User not found")
    if not crud.user.is_superuser(current_user) and (user.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return user


