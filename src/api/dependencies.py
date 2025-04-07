"""API dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dummy.application.services.dummy_service import DummyService
from src.dummy.domain.event_publisher.interfaces.event_publisher import (
    EventPublisher,
)
from src.dummy.domain.repositories.interfaces.dummy_repository import (
    DummyRepository,
)
from src.dummy.infrastructure.event_publisher.console.console_publisher import (
    ConsoleEventPublisher,
)
from src.dummy.infrastructure.repositories.postgresql.dummy_repository import (
    PostgreSQLDummyRepository,
)
from src.shared.database.dependencies import get_db_session


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
