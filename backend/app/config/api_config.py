from typing import Optional
from pydantic import BaseSettings


class APISettings(BaseSettings):
    DJANGO_POSTGRES_DB_ENGINE: Optional[str] = "django.db.backends.postgresql"
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

api_settings = APISettings()