from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.exceptions import APIErrorMessage

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    error_response = APIErrorMessage()
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        error_response.message = "Incorrect email or password"
        raise HTTPException(status_code=400, detail=error_response.dict())
    elif not crud.user.is_active(user):
        error_response.message = "Inactive user"
        raise HTTPException(status_code=400, detail="Inactive user")
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
    user_id: str = Body(...),
    mode: str = Body(...),  # email or SMS
    db: Session = Depends(deps.get_db),
) -> Any:
    """ """
    user = crud.user.get_by_uuid(db=db, uuid=user_id)
    otp = crud.otp.create_with_owner(
        db=db, obj_in=models.OTPCreate(user_id=user.uuid), user=user
    )
    is_otp_message_sent = crud.otp.send_otp(db=db, user=user)
    if not is_otp_message_sent:
        raise HTTPException(
            status_code=400,
            detail="Sorry, we had trouble sending your verification code. Please try again",
        )
    response = {
        "success": is_otp_message_sent,
        "otp": otp,
    }
    return response


@router.post("/login/test-token", response_model=schemas.User)
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
