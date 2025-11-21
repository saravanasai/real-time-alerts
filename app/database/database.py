from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker,  declarative_base
from app.config import Config
from sqlalchemy.pool import NullPool

DATABASE_URL = Config.CONNECTION_URL


SYNC_DATABASE_URL = DATABASE_URL

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "application_name": "my_app_sync",
        "connect_timeout": 10,
    }
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = DATABASE_URL

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: ""
    }
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


Base = declarative_base()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as as_session:
        try:
            yield as_session
        finally:
            await as_session.close()


def get_db() -> Generator:
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
