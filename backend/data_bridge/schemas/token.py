from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: Optional[str] = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None  # subject (user's uuid)
