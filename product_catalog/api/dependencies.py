"""API dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from product_catalog.application.services.dummy_service import DummyService
from product_catalog.infrastructure.database.dependencies import get_db_session
from product_catalog.infrastructure.event_publisher.console.console_publisher import (
    ConsoleEventPublisher,
)
from product_catalog.infrastructure.event_publisher.interfaces.event_publisher import (
    EventPublisher,
)
from product_catalog.infrastructure.repositories.interfaces.dummy_repository import (
    DummyRepository,
)
from product_catalog.infrastructure.repositories.postgresql.dummy_repository import (
    PostgreSQLDummyRepository,
)


def get_dummy_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DummyRepository:
    """
    Get the dummy repository.

    Args:
        session: The database session

    Returns:
        PostgreSQLDummyRepository instance
    """
    return PostgreSQLDummyRepository(session=session)


def get_event_publisher() -> EventPublisher:
    """
    Get the event publisher.

    Returns:
        ConsoleEventPublisher instance
    """
    return ConsoleEventPublisher()


def get_dummy_service(
    repository: DummyRepository = Depends(get_dummy_repository),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> DummyService:
    """
    Get the dummy service.

    Args:
        repository: The repository for dummy entities
        event_publisher: The event publisher

    Returns:
        DummyService instance
    """
    return DummyService(repository, event_publisher)
