"""API lifespan setup."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from product_catalog.db.models import load_all_models
from product_catalog.settings import settings


def _setup_db(app: FastAPI) -> None:
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    Args:
        app: FastAPI application
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for the FastAPI application.

    This function is called when the application starts up and shuts down.
    It's used to set up and tear down resources.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    # Load all database models to ensure they're registered with SQLAlchemy
    load_all_models()

    # Setup database connection
    _setup_db(app)

    yield

    # Clean up resources when the application shuts down
    await app.state.db_engine.dispose()
