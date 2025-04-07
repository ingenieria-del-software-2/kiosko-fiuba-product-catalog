"""Product repository interface."""

import uuid
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductFilterDTO,
    ProductUpdateDTO,
)
from src.products.domain.entities.product import Product


class ProductRepository(ABC):
    """Interface for product repository."""

    @abstractmethod
    async def create(self, product_dto: ProductCreateDTO) -> Product:
        """Create a new product.

        Args:
            product_dto: DTO with product data

        Returns:
            Created product entity
        """

    @abstractmethod
    async def get_by_id(self, product_id: uuid.UUID) -> Optional[Product]:
        """Get a product by its ID.

        Args:
            product_id: Product ID

        Returns:
            Product entity or None if not found
        """

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by its SKU.

        Args:
            sku: Product SKU

        Returns:
            Product entity or None if not found
        """

    @abstractmethod
    async def update(
        self,
        product_id: uuid.UUID,
        product_dto: ProductUpdateDTO,
    ) -> Optional[Product]:
        """Update a product.

        Args:
            product_id: Product ID
            product_dto: DTO with updated product data

        Returns:
            Updated product entity or None if not found
        """

    @abstractmethod
    async def delete(self, product_id: uuid.UUID) -> bool:
        """Delete a product.

        Args:
            product_id: Product ID

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    async def list(
        self,
        filters: Optional[ProductFilterDTO] = None,
    ) -> Tuple[List[Product], int]:
        """List products with optional filtering.

        Args:
            filters: Optional filtering parameters

        Returns:
            List of product entities and total count
        """
