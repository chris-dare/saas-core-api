from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from data_bridge.core.config import settings

async_db_url = settings.DJANGO_EMR_SQLALCHEMY_DATABASE_URI
AsyncSessionLocal: AsyncSession = sessionmaker(
    create_async_engine(
        settings.DJANGO_EMR_SQLALCHEMY_DATABASE_URI, echo=True, future=True
    ),
    class_=AsyncSession,
    expire_on_commit=False,
)
