from typing import List, Optional

from app.core.config import OAuthScopeType
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: Optional[str] = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None  # subject (user's uuid)
    scopes: Optional[List[OAuthScopeType]] = []
