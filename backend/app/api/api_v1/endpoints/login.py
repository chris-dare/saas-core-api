from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.exceptions import get_api_error_message, ErrorCode
from app.utils.messaging import ModeOfMessageDelivery

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: Session = Depends(deps.get_async_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail=get_api_error_message(error_code=ErrorCode.INCORRECT_EMAIL_OR_PASSWORD)
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=400,
            detail=get_api_error_message(error_code=ErrorCode.INACTIVE_USER)
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            subject=user.uuid, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post(
    "/auth/generate-otp",
)
def generate_otp(
    email: str = Body(...),
    mode: str = Body(...),  # email or SMS
    db: Session = Depends(deps.get_db),
) -> Any:
    """Generates an OTP for 2FA or user verification/activation"""
    user = crud.user.get_by_email(db=db, email=email)
    otp = crud.otp.create_with_owner(
        db=db, obj_in=models.OTPCreate(user_id=user.uuid), user=user
    )
    is_otp_message_sent = False
    is_otp_message_sent = crud.otp.send_otp(db=db, user=user, otp=otp, mode=ModeOfMessageDelivery.EMAIL)
    response = {
        "success": is_otp_message_sent,
        "otp": otp, # TODO: Exclude from API once Twilio funding is secured
    }
    return response

@router.get("/auth/verify-user-status", response_model=models.UserPublicRead)
def verify_user_status(
    email: Optional[EmailStr] = None,
    mobile: Optional[str] = None,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Verifies user status"""
    if not email and not mobile:
        raise HTTPException(
            status_code=400,
            detail=get_api_error_message(error_code=ErrorCode.MISSING_EMAIL_OR_MOBILE),
        )
    if email:
        user = crud.user.get_by_email(db=db, email=email)
    if mobile:
        user = crud.user.get_by_mobile(db=db, mobile=mobile)
    if not user:
        raise HTTPException(
            status_code=400,
            detail=get_api_error_message(error_code=ErrorCode.USER_NOT_FOUND),
        )
    return user


@router.post("/login/test-token", response_model=models.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    raise NotImplementedError


@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    raise NotImplementedError
