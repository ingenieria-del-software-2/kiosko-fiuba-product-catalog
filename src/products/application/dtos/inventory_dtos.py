"""Inventory Data Transfer Objects."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class InventoryCreateDTO:
    """DTO for creating a new inventory record."""

    product_id: UUID
    quantity: int
    reorder_threshold: Optional[int] = None
    reorder_quantity: Optional[int] = None


@dataclass
class InventoryUpdateDTO:
    """DTO for updating an existing inventory record."""

    id: UUID
    quantity: Optional[int] = None
    reorder_threshold: Optional[int] = None
    reorder_quantity: Optional[int] = None


@dataclass
class InventoryResponseDTO:
    """DTO for inventory responses."""

    id: UUID
    product_id: UUID
    quantity: int
    status: str
    reorder_threshold: Optional[int]
    reorder_quantity: Optional[int]
    created_at: datetime
    updated_at: datetime
