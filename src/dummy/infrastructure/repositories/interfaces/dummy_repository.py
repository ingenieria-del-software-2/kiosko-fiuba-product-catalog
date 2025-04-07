"""Dummy repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.dummy.domain.model.dummy import Dummy


class DummyRepository(ABC):
    """Repository interface for Dummy entities."""

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> List[Dummy]:
        """
        Get all dummy entities with pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of Dummy entities
        """

    @abstractmethod
    async def get_by_id(self, dummy_id: int) -> Optional[Dummy]:
        """
        Get a dummy entity by its ID.

        Args:
            dummy_id: ID of the dummy entity

        Returns:
            Dummy entity if found, None otherwise
        """

    @abstractmethod
    async def create(self, dummy: Dummy) -> Dummy:
        """
        Create a new dummy entity.

        Args:
            dummy: Dummy entity to create

        Returns:
            Created dummy entity with ID
        """

    @abstractmethod
    async def find_by_name(self, name: str) -> List[Dummy]:
        """
        Find dummy entities by name.

        Args:
            name: Name to search for

        Returns:
            List of matching Dummy entities
        """
