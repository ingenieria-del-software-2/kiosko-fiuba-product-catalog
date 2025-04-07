"""FastAPI dependencies for dependency injection."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dummy.application.services.dummy_service import DummyService
from src.dummy.domain.event_publisher.interfaces.event_publisher import (
    EventPublisher as DummyEventPublisher,
)
from src.dummy.domain.repositories.interfaces.dummy_repository import DummyRepository
from src.dummy.infrastructure.event_publisher.console.console_publisher import (
    ConsoleEventPublisher as DummyConsoleEventPublisher,
)
from src.dummy.infrastructure.repositories.postgresql.dummy_repository import (
    PostgreSQLDummyRepository,
)
from src.products.application.services.product_service import ProductService
from src.products.domain.event_publisher.event_publisher import EventPublisher
from src.products.domain.repositories.category_repository import CategoryRepository
from src.products.domain.repositories.product_repository import ProductRepository
from src.products.infrastructure.repositories.postgresql.product_repository import (
    PostgresProductRepository,
)
from src.shared.database.dependencies import get_db_session
from src.shared.event_publisher.console_publisher import ConsoleEventPublisher

# Dummy Repository dependencies


def get_dummy_repository(
    session: AsyncSession = Depends(get_db_session),
) -> DummyRepository:
    """Get dummy repository implementation."""
    return PostgreSQLDummyRepository(session=session)


def get_dummy_event_publisher() -> DummyEventPublisher:
    """Get dummy event publisher implementation."""
    return DummyConsoleEventPublisher()


def get_dummy_service(
    repository: DummyRepository = Depends(get_dummy_repository),
    event_publisher: DummyEventPublisher = Depends(get_dummy_event_publisher),
) -> DummyService:
    """Get dummy service implementation."""
    return DummyService(repository=repository, event_publisher=event_publisher)


# Repository dependencies


async def get_product_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ProductRepository:
    """Get product repository implementation."""
    return PostgresProductRepository(session)


async def get_category_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CategoryRepository:
    """Get category repository implementation."""
    # This would be replaced with the actual implementation
    # For now we'll use a placeholder
    from src.products.infrastructure.repositories.postgresql import (
        category_repository,
    )

    return category_repository.PostgresCategoryRepository(session)


# Event publisher dependencies


async def get_event_publisher() -> EventPublisher:
    """Get event publisher implementation."""
    # Using the shared console publisher for all events
    return ConsoleEventPublisher()


# Service dependencies


async def get_product_service(
    product_repository: ProductRepository = Depends(get_product_repository),
    category_repository: CategoryRepository = Depends(get_category_repository),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> ProductService:
    """Get product service implementation."""
    return ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
        event_publisher=event_publisher,
    )
