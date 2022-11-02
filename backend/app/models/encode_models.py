"""The :mod:`app.models.user` module contains a ORMs used to persist and retrieve 
data concerning users on HyperSenta
"""
# Author: Christopher Dare

import orm

from typing import Optional
from app.config.api_config import api_settings


class User(orm.Model):
    tablename = "user"
    registry = api_settings.DEFAULT_MODEL_REGISTRY
    fields = {
        "id": orm.Integer(primary_key=True),
        "first_name": orm.String(max_length=100),
        "last_name": orm.String(max_length=100),
        "other_names": orm.String(max_length=100),
        "name": orm.String(max_length=100),
        "is_active": orm.Boolean(default=False),
        "is_expert": orm.Boolean(default=False),
    }