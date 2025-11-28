from typing import AsyncGenerator, Generator

import redis.asyncio as redis
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
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

# Redis async client
_redis_client = None


async def get_cache() -> redis.Redis:
    """Get async Redis client (connection pooling handled automatically)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            decode_responses=True,
            socket_keepalive=True,
            max_connections=50,
            socket_connect_timeout=5,  # Connection timeout
            socket_timeout=5,  # Read timeout
            retry_on_timeout=True,  # Auto-retry on timeout
            health_check_interval=30  # Check connection health every 30s
        )
    return _redis_client


async def close_redis():
    """Close Redis connection on app shutdown."""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


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
