from datetime import timedelta
from typing import Any, Optional
from logging import getLogger

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app import crud, models
from app.api import deps
from app.core import security
from app.core.config import settings
from app.exceptions import get_api_error_message, ErrorCode
from app.utils import ModeOfMessageDelivery, parse_mobile_number

router = APIRouter()
logger = getLogger(__name__)


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_async_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        db, mobile=form_data.username, password=form_data.password
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
    "/generate-otp",
)
async def generate_otp(
    otp_in: models.OTPCreate,
    db: AsyncSession = Depends(deps.get_async_db),
) -> Any:
    """Generates an OTP for 2FA, user verification, password reset, etc."""
    try:
        user = await crud.user.get_by_email(db, email=otp_in.email)
        if not user:
            logger.error(f"User with email {otp_in.email} not found")
            raise HTTPException(
                status_code=400,
                detail=get_api_error_message(error_code=ErrorCode.USER_NOT_FOUND)
            )
        otp = await crud.otp.create_with_owner(
            db=db, obj_in=otp_in, user=user,
        )
        client_response = await crud.otp.send_otp(
            db=db, user=user, otp=otp, mode=otp_in.mode, token_type=otp_in.token_type
        )
        response = {
            "success": client_response.is_sent,
            "message": client_response.message,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response

@router.get("/verify-user-status", response_model=models.UserPublicRead)
async def verify_user_status(
    email: Optional[EmailStr] = None,
    mobile: Optional[str] = None,
    db: AsyncSession = Depends(deps.get_async_db),
) -> Any:
    """Verifies whether a user exists or is active"""
    if not email and not mobile:
        raise HTTPException(
            status_code=400,
            detail=get_api_error_message(error_code=ErrorCode.MISSING_EMAIL_OR_MOBILE),
        )
    if mobile:
        try:
            mobile = parse_mobile_number(mobile)
            user = await crud.user.get_by_mobile(db=db, mobile=mobile)
        except ValueError as e:
            user = None
    elif email:
        user = await crud.user.get_by_email(db=db, email=email)
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


@router.post("/reset-password/", response_model=None)
async def reset_password(
    payload: models.PasswordResetOTPPayload,
    db: AsyncSession = Depends(deps.get_async_db),
) -> Any:
    """
    Resets a user's password based on a token sent to them via email or sms
    """
    is_password_changed = False
    try:
        is_password_changed = await crud.user.change_password(
            db=db, token=payload.token, new_password=payload.new_password, confirm_password=payload.confirm_password
        )
        if is_password_changed: message = "Password updated successfully"
    except ValueError as e:
        message = str(e)
    return {
            "success": is_password_changed,
            "message": message,
        }