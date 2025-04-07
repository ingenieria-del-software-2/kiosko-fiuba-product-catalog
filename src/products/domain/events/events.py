"""Domain events for the Product Catalog domain."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""

    event_id: UUID
    event_type: str
    aggregate_id: UUID
    occurred_on: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ProductCreatedEvent(DomainEvent):
    """Event raised when a product is created."""

    product_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the event after initialization."""
        if not self.product_data:
            raise ValueError("product_data cannot be empty")


@dataclass(frozen=True)
class ProductUpdatedEvent(DomainEvent):
    """Event raised when a product is updated."""

    product_data: Dict[str, Any] = field(default_factory=dict)
    previous_data: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validate the event after initialization."""
        if not self.product_data:
            raise ValueError("product_data cannot be empty")


@dataclass(frozen=True)
class ProductDeletedEvent(DomainEvent):
    """Event raised when a product is deleted."""

    product_data: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class CategoryCreatedEvent(DomainEvent):
    """Event raised when a category is created."""

    category_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the event after initialization."""
        if not self.category_data:
            raise ValueError("category_data cannot be empty")


@dataclass(frozen=True)
class CategoryUpdatedEvent(DomainEvent):
    """Event raised when a category is updated."""

    category_data: Dict[str, Any] = field(default_factory=dict)
    previous_data: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validate the event after initialization."""
        if not self.category_data:
            raise ValueError("category_data cannot be empty")


@dataclass(frozen=True)
class CategoryDeletedEvent(DomainEvent):
    """Event raised when a category is deleted."""

    category_data: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class InventoryUpdatedEvent(DomainEvent):
    """Event raised when inventory is updated."""

    inventory_data: Dict[str, Any] = field(default_factory=dict)
    previous_quantity: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate the event after initialization."""
        if not self.inventory_data:
            raise ValueError("inventory_data cannot be empty")
