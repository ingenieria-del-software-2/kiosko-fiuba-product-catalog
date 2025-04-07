"""Configuration for product repository tests."""

from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.shared.database.base import Base


# Use function scope for all fixtures - no shared state between tests
@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a SQLAlchemy engine for testing."""
    # Use SQLite for tests with enable_parentheses_parsing to handle more complex SQL
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={
            "check_same_thread": False,  # Allow multi-threaded access
        },
        # Don't echo all SQL for cleaner test output
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Dispose of the engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a SQLAlchemy session for testing.

    This fixture creates an isolated session for each test with its own transaction
    that is rolled back at the end to prevent test data from persisting.
    """
    # Create a session factory that's bound to our engine with better async support
    session_factory = async_sessionmaker(
        bind=db_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        # Make sure future is used for SQLAlchemy 2.0 compatibility
        future=True,
    )

    # Create a new session for each test
    session = session_factory()

    # Start a transaction
    async with session.begin() as transaction:
        # Give the session to the test
        yield session

        # Always roll back at the end
        await transaction.rollback()
