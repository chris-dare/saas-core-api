from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.PATIENT_PORTAL_SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_db_url = settings.PATIENT_PORTAL_SQLALCHEMY_DATABASE_URI
AsyncSessionLocal: AsyncSession = sessionmaker(
    create_async_engine(
        settings.PATIENT_PORTAL_SQLALCHEMY_DATABASE_URI, echo=True, future=True
    ),
    class_=AsyncSession,
    expire_on_commit=False,
)