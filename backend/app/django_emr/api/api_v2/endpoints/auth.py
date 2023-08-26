from datetime import timedelta
from logging import getLogger
from typing import Any

from django_emr.api import deps as django_emr_deps
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import schemas
from app.core import security
from app.core.config import settings
from app.django_emr import crud, models
from app.exceptions import ErrorCode, get_api_error_message
from app.utils import ModeOfMessageDelivery

router = APIRouter()
logger = getLogger(__name__)


@router.post("/access-token", response_model=schemas.Token)
async def login_access_token(
    db: Session = Depends(django_emr_deps.get_async_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
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
            detail=get_api_error_message(
                error_code=ErrorCode.INCORRECT_EMAIL_OR_PASSWORD
            ),
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=400,
            detail=get_api_error_message(error_code=ErrorCode.INACTIVE_USER),
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            subject=user.uuid, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
