"""The :mod:`app.models.user` module contains a ORMs used to persist and retrieve 
data concerning users on HyperSenta
"""
# Author: Christopher Dare

import orm

from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None,  primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None