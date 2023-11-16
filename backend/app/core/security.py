from datetime import datetime, timedelta
from random import randint
from typing import Any, List, Union

from app import models
from app.core.config import OAuthScopeType, settings
from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any],
    user: models.User,
    expires_delta: timedelta = None,
    scopes: List[OAuthScopeType] = None,
) -> str:
    # check whether the user is authorized to use the scopes they are requesting for
    unauthorized_scopes = [
        _scope for _scope in scopes if _scope not in user.oauth2_scopes.split()
    ]
    if unauthorized_scopes:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Not enough permissions. {unauthorized_scopes} are not granted to user",
        )
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "scopes": scopes}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_otp_code(n=6):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)
