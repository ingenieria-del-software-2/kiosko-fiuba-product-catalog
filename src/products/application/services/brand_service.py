"""Brand service for application layer."""

import uuid
from typing import List, Optional, Tuple

from src.products.application.dtos.product_dtos import (
    BrandCreateDTO,
    BrandUpdateDTO,
)
from src.products.domain.entities.product import Brand
from src.products.domain.repositories.brand_repository import BrandRepository


class BrandService:
    """Service for brand operations."""

    def __init__(self, brand_repository: BrandRepository) -> None:
        """Initialize service with repository.

        Args:
            brand_repository: Repository for brand operations
        """
        self._brand_repository = brand_repository

    async def create_brand(self, brand_data: BrandCreateDTO) -> Brand:
        """Create a new brand.

        Args:
            brand_data: DTO with brand data

        Returns:
            Created brand entity
        """
        return await self._brand_repository.create(brand_data)

    async def get_brand_by_id(self, brand_id: uuid.UUID) -> Optional[Brand]:
        """Get a brand by its ID.

        Args:
            brand_id: Brand ID

        Returns:
            Brand entity or None if not found
        """
        return await self._brand_repository.get_by_id(brand_id)

    async def get_brand_by_name(self, name: str) -> Optional[Brand]:
        """Get a brand by its name.

        Args:
            name: Brand name

        Returns:
            Brand entity or None if not found
        """
        return await self._brand_repository.get_by_name(name)

    async def update_brand(
        self,
        brand_id: uuid.UUID,
        brand_data: BrandUpdateDTO,
    ) -> Optional[Brand]:
        """Update a brand.

        Args:
            brand_id: Brand ID
            brand_data: DTO with updated brand data

        Returns:
            Updated brand entity or None if not found
        """
        return await self._brand_repository.update(brand_id, brand_data)

    async def delete_brand(self, brand_id: uuid.UUID) -> bool:
        """Delete a brand.

        Args:
            brand_id: Brand ID

        Returns:
            True if deleted, False if not found
        """
        return await self._brand_repository.delete(brand_id)

    async def list_brands(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Brand], int]:
        """List brands with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of brand entities and total count
        """
        return await self._brand_repository.list(limit, offset)
