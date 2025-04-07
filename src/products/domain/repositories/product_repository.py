"""Product repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.products.domain.model.product import Product


class ProductRepository(ABC):
    """Interface for product repository operations."""

    @abstractmethod
    async def create(self, product: Product) -> Product:
        """Create a new product."""

    @abstractmethod
    async def update(self, product: Product) -> Product:
        """Update an existing product."""

    @abstractmethod
    async def delete(self, product_id: UUID) -> bool:
        """Delete a product by ID."""

    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get a product by ID."""

    @abstractmethod
    async def list_products(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        """List products with pagination."""

    @abstractmethod
    async def search_products(
        self,
        query: str,
        category_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        """Search products by name, description or category."""

    @abstractmethod
    async def get_by_category(
        self,
        category_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        """Get products by category ID."""
