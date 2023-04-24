from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
async_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("postgresql", "postgresql+asyncpg")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal: AsyncSession = sessionmaker(
    create_async_engine(async_db_url, echo=True, future=True), 
    class_=AsyncSession, expire_on_commit=False
)
