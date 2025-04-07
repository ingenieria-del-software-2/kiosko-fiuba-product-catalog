"""Database dependencies."""

import logging
from typing import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.shared.database.connection import get_session_factory

logger = logging.getLogger(__name__)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    Args:
        request: Current request

    Yields:
        Database session
    """
    try:
        # First try to get session from app state
        try:
            session: AsyncSession = request.app.state.db_session_factory()
        except (AttributeError, KeyError):
            # Fall back to creating a new session if not in app state
            session_factory = get_session_factory()
            session = session_factory()

        try:
            await session.execute(
                text("SET statement_timeout = 10000"),
            )  # 10 seconds timeout
            yield session
        finally:
            await session.commit()
            await session.close()
    except Exception as e:
        # Log the error but don't expose details to client
        logger.error(f"Database session error: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        ) from e
