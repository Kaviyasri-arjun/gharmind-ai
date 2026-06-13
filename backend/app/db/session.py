"""
GHARMIND AI — Async Database Session
SQLAlchemy 2.0 async engine with pgvector support.
"""
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)

# ── Engine creation ────────────────────────────────────────────────────

def _create_engine() -> AsyncEngine:
    """Create the async SQLAlchemy engine."""
    engine_kwargs: dict[str, Any] = {
        "echo": settings.DEBUG,
        "echo_pool": False,
        "future": True,
    }

    # Use NullPool for tests to avoid connection issues
    if settings.APP_ENV == "testing":
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
        engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        engine_kwargs["pool_timeout"] = settings.DATABASE_POOL_TIMEOUT
        engine_kwargs["pool_pre_ping"] = True

    return create_async_engine(settings.DATABASE_URL, **engine_kwargs)


engine: AsyncEngine = _create_engine()

# ── Session factory ────────────────────────────────────────────────────

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ── Dependency ─────────────────────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.
    Automatically handles commit/rollback/close.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Health check ───────────────────────────────────────────────────────

async def check_database_health() -> bool:
    """Verify database connectivity."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        return False


async def init_db_extensions() -> None:
    """Initialize PostgreSQL extensions required by the application."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        logger.info("database_extensions_initialized")
