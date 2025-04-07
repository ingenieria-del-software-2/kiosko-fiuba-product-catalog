"""Database dependencies."""

import logging
from asyncio import current_task
from typing import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.shared.database.connection import get_session_factory

logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session for the request.

    Yields:
        Database session
    """
    try:
        # Get session factory and create scoped session
        session_factory = get_session_factory()
        scoped_factory = async_scoped_session(
            session_factory,
            scopefunc=current_task,
        )
        session = scoped_factory()

        try:
            # Start a transaction
            await session.begin()

            # Set statement timeout
            try:
                await session.execute(text("SET statement_timeout = 30000"))
            except Exception as e:
                logger.warning(f"Failed to set statement timeout: {e}")

            # Yield the session to the request handler
            yield session

            # After the request is processed
            await session.commit()

        except Exception as e:
            logger.error(f"Database session error: {e!s}", exc_info=True)
            # Try to roll back the transaction
            try:
                await session.rollback()
            except Exception as rb_error:
                logger.error(f"Rollback error: {rb_error!s}")
            raise
        finally:
            # Always clean up resources
            await session.close()
            await scoped_factory.remove()

    except Exception as e:
        logger.error(f"Database connection error: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        ) from e
