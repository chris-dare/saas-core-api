from typing import Optional

from pydantic import BaseModel

class GenericValueset(BaseModel):
    name: str
    description: Optional[str] = None
    choices: list[str]