"""Database connection utilities."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.settings import settings


def get_engine() -> AsyncEngine:
    """
    Create database engine.

    Returns:
        SQLAlchemy async engine instance
    """
    return create_async_engine(str(settings.db_url), echo=settings.db_echo)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Create session factory.

    Returns:
        SQLAlchemy async session factory
    """
    engine = get_engine()
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
