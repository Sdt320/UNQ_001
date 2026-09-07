"""Database session management and asynchronous engine configuration."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import logger

Base = declarative_base()

# Configure Async Engine
database_url = settings.DATABASE_URL
if "sqlite" in database_url and not database_url.startswith("sqlite+aiosqlite"):
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")

# Enable pooling arguments only for postgresql
connect_args = {}
if "sqlite" in database_url:
    connect_args = {"check_same_thread": False}

async_engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initializes database tables and extensions."""
    async with async_engine.begin() as conn:
        try:
            # Enable PostGIS and uuid-ossp extensions if connected to PostgreSQL
            if "postgresql" in settings.DATABASE_URL:
                from sqlalchemy import text
                await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
                await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "postgis";'))
        except Exception as e:
            logger.warning(f"Extension init skipped or not supported: {e}")
        
        # Import models to ensure they are registered with Base metadata
        from app.database import models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified/created successfully.")
