"""Brand repository interface."""

import uuid
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from src.products.application.dtos.product_dtos import (
    BrandCreateDTO,
    BrandUpdateDTO,
)
from src.products.domain.entities.product import Brand


class BrandRepository(ABC):
    """Interface for brand repository."""

    @abstractmethod
    async def create(self, brand_dto: BrandCreateDTO) -> Brand:
        """Create a new brand.

        Args:
            brand_dto: DTO with brand data

        Returns:
            Created brand entity
        """

    @abstractmethod
    async def get_by_id(self, brand_id: uuid.UUID) -> Optional[Brand]:
        """Get a brand by its ID.

        Args:
            brand_id: Brand ID

        Returns:
            Brand entity or None if not found
        """

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Brand]:
        """Get a brand by its name.

        Args:
            name: Brand name

        Returns:
            Brand entity or None if not found
        """

    @abstractmethod
    async def update(
        self,
        brand_id: uuid.UUID,
        brand_dto: BrandUpdateDTO,
    ) -> Optional[Brand]:
        """Update a brand.

        Args:
            brand_id: Brand ID
            brand_dto: DTO with updated brand data

        Returns:
            Updated brand entity or None if not found
        """

    @abstractmethod
    async def delete(self, brand_id: uuid.UUID) -> bool:
        """Delete a brand.

        Args:
            brand_id: Brand ID

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> Tuple[List[Brand], int]:
        """List brands with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of brand entities and total count
        """
