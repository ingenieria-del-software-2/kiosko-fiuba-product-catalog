"""Category repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.products.domain.model.category import Category


class CategoryRepository(ABC):
    """Interface for category repository operations."""

    @abstractmethod
    async def create(self, category: Category) -> Category:
        """Create a new category."""

    @abstractmethod
    async def update(self, category: Category) -> Category:
        """Update an existing category."""

    @abstractmethod
    async def delete(self, category_id: UUID) -> bool:
        """Delete a category by ID."""

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """Get a category by ID."""

    @abstractmethod
    async def list_categories(
        self,
        parent_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Category]:
        """List categories with optional parent filter and pagination."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Category]:
        """Get a category by name."""
