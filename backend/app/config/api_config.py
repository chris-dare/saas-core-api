from typing import Optional
from pydantic import BaseSettings

import orm, databases


class APISettings(BaseSettings):
    DJANGO_POSTGRES_DB_ENGINE: Optional[str] = "django.db.backends.postgresql"
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DEFAULT_DB: Optional[databases.Database] = None
    DEFAULT_MODEL_REGISTRY: Optional[orm.ModelRegistry] = None

api_settings = APISettings()

api_settings.DEFAULT_DB = databases.Database(f"postgresql://{api_settings.POSTGRES_USER}:{api_settings.POSTGRES_PASSWORD}@{api_settings.POSTGRES_SERVER}:{api_settings.POSTGRES_PORT}/{api_settings.POSTGRES_DB}")
api_settings.DEFAULT_MODEL_REGISTRY = orm.ModelRegistry(database=api_settings.DEFAULT_DB)