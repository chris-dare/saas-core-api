from typing import Optional

from pydantic import BaseModel


class APIErrorMessage(BaseModel):
    message: str = "Sorry, an error occurred whilst processing your request"
    success: bool = False
    status_code: int = 400
    errors: Optional[list[dict]] = None
