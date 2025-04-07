"""Inventory entity module for the Product Catalog domain."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.products.domain.model.value_objects import InventoryStatus


@dataclass(frozen=True)
class Inventory:
    """Inventory entity representing stock for a product."""

    product_id: UUID
    quantity: int
    id: UUID = field(default_factory=uuid4)
    status: InventoryStatus = InventoryStatus.IN_STOCK
    reorder_threshold: Optional[int] = None
    reorder_quantity: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate inventory attributes."""
        object.__setattr__(self, "status", self._calculate_status())

    def _calculate_status(self) -> InventoryStatus:
        """Calculate inventory status based on quantity and threshold."""
        if self.quantity <= 0:
            return InventoryStatus.OUT_OF_STOCK
        if self.reorder_threshold and self.quantity <= self.reorder_threshold:
            return InventoryStatus.LOW_STOCK
        return InventoryStatus.IN_STOCK

    def is_available(self) -> bool:
        """Check if the product is available in inventory."""
        return self.quantity > 0
