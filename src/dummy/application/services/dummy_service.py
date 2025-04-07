"""Application service for the dummy domain."""

from typing import List, Optional

from src.dummy.application.dtos.dummy_dtos import CreateDummyDTO, DummyDTO
from src.dummy.domain.event_publisher.interfaces.event_publisher import (
    EventPublisher,
)
from src.dummy.domain.events.events import DummyCreatedEvent
from src.dummy.domain.exceptions.domain_exceptions import DummyNotFoundError
from src.dummy.domain.model.dummy import Dummy
from src.dummy.domain.repositories.interfaces.dummy_repository import (
    DummyRepository,
)


class DummyService:
    """Service for managing dummy entities."""

    def __init__(
        self,
        repository: DummyRepository,
        event_publisher: Optional[EventPublisher] = None,
    ) -> None:
        """
        Initialize the service with a repository and event publisher.

        Args:
            repository: Repository for dummy entities
            event_publisher: Publisher for domain events
        """
        self._repository = repository
        self._event_publisher = event_publisher

    async def get_all_dummies(self, limit: int = 10, offset: int = 0) -> List[DummyDTO]:
        """
        Get all dummy entities with pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of DummyDTO objects
        """
        dummies = await self._repository.get_all(limit=limit, offset=offset)
        return [
            DummyDTO(id=dummy.id, name=dummy.name)
            for dummy in dummies
            if dummy.id is not None
        ]

    async def create_dummy(self, dto: CreateDummyDTO) -> DummyDTO:
        """
        Create a new dummy entity.

        Args:
            dto: DTO with data for the new entity

        Returns:
            DTO of the created entity
        """
        dummy = Dummy(name=dto.name)
        created_dummy = await self._repository.create(dummy)

        # Ensure ID is not None
        if created_dummy.id is None:
            raise ValueError("Failed to create dummy with valid ID")

        # Publish event if event publisher is available
        if self._event_publisher:
            event = DummyCreatedEvent(
                dummy_id=created_dummy.id,
                name=created_dummy.name,
            )
            await self._event_publisher.publish(event)

        return DummyDTO(id=created_dummy.id, name=created_dummy.name)

    async def get_dummy_by_id(self, dummy_id: int) -> DummyDTO:
        """
        Get a dummy entity by its ID.

        Args:
            dummy_id: ID of the entity to get

        Returns:
            DTO of the entity

        Raises:
            DummyNotFoundError: If the entity is not found
        """
        dummy = await self._repository.get_by_id(dummy_id)
        if not dummy:
            raise DummyNotFoundError(f"Dummy with ID {dummy_id} not found")

        # Ensure ID is not None (this should never happen, but we check for type safety)
        if dummy.id is None:
            raise ValueError(f"Dummy found but has no ID: {dummy}")

        return DummyDTO(id=dummy.id, name=dummy.name)

    async def find_dummies_by_name(self, name: str) -> List[DummyDTO]:
        """
        Find dummy entities by name.

        Args:
            name: Name to search for

        Returns:
            List of matching DummyDTO objects
        """
        dummies = await self._repository.find_by_name(name)
        return [
            DummyDTO(id=dummy.id, name=dummy.name)
            for dummy in dummies
            if dummy.id is not None
        ]
