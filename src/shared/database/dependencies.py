"""Database dependencies."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    Args:
        request: Current request

    Yields:
        Database session
    """
    try:
        session: AsyncSession = request.app.state.db_session_factory()

        try:
            yield session
        finally:
            await session.commit()
            await session.close()
    except (AttributeError, KeyError):
        # For testing purposes - allow dependency injection to override this
        yield None
