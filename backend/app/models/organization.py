"""The :mod:`app.models.organization` module contains a ORMs used to persist and retrieve 
data concerning organizations on HyperSenta
"""
# Author: Christopher Dare

from app.config.api_config import api_settings
import orm


class Organization(orm.Model):
    tablename = "organization"
    registry = api_settings.DEFAULT_MODEL_REGISTRY
    fields = {
        "id": orm.Integer(primary_key=True),
        "name": orm.String(max_length=100),
        "owner": orm.String(max_length=100), # TODO
        "is_active": orm.Boolean(default=False),
    }
