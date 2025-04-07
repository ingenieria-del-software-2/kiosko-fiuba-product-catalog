"""Inventory repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.products.domain.model.inventory import Inventory


class InventoryRepository(ABC):
    """Interface for inventory repository operations."""

    @abstractmethod
    async def create(self, inventory: Inventory) -> Inventory:
        """Create a new inventory record."""

    @abstractmethod
    async def update(self, inventory: Inventory) -> Inventory:
        """Update an existing inventory record."""

    @abstractmethod
    async def get_by_id(self, inventory_id: UUID) -> Optional[Inventory]:
        """Get inventory by ID."""

    @abstractmethod
    async def get_by_product_id(self, product_id: UUID) -> Optional[Inventory]:
        """Get inventory by product ID."""

    @abstractmethod
    async def list_low_stock(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Inventory]:
        """List products with low stock."""

    @abstractmethod
    async def update_quantity(
        self,
        product_id: UUID,
        quantity_change: int,
    ) -> Optional[Inventory]:
        """Update inventory quantity by the specified amount.

        Args:
            product_id: ID of the product to update
            quantity_change: Amount to change quantity by (positive or negative)

        Returns:
            Updated inventory record or None if not found
        """
