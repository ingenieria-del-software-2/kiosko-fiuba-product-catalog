"""Database connection utilities."""

import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.settings import settings

logger = logging.getLogger(__name__)

# Create engine only once at module import time
_engine = None
_session_factory = None


def get_engine() -> AsyncEngine:
    """
    Create database engine.

    Returns:
        SQLAlchemy async engine instance
    """
    global _engine  # noqa: PLW0603
    if _engine is None:
        try:
            # Create engine with greenlet support and connection pooling
            _engine = create_async_engine(
                str(settings.db_url),
                echo=settings.db_echo,
                # Add pool settings
                pool_pre_ping=True,
                pool_size=20,
                max_overflow=10,
                # Add explicit execution options
                execution_options={"isolation_level": "READ COMMITTED"},
                # This is crucial for greenlet support
                future=True,
            )
            logger.info("Database engine created successfully")
        except Exception as e:
            logger.error(f"Failed to create database engine: {e!s}")
            raise
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Create session factory.

    Returns:
        SQLAlchemy async session factory
    """
    global _session_factory  # noqa: PLW0603
    if _session_factory is None:
        try:
            engine = get_engine()
            # Configure session factory with appropriate settings
            _session_factory = async_sessionmaker(
                engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
            logger.info("Session factory created successfully")
        except Exception as e:
            logger.error(f"Failed to create session factory: {e!s}")
            raise
    return _session_factory
