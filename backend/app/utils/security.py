"""The :mod:`app.utils.security` module contains resuable utils for security operations for web APIs
"""
# Author: Christopher Dare

import hashlib
from typing import Optional

from app.core.config import settings
from jose import jwt


def make_password(raw_password: str) -> str:
    assert raw_password
    hash = hashlib.md5(raw_password.encode("utf-8")).hexdigest()
    return hash


def check_password(hash: str, raw_password: str) -> bool:
    """Generates the hash for a raw_password and compares it."""
    generated_hash = make_password(raw_password)
    return hash == generated_hash


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["email"]
    except jwt.JWTError:
        return None
