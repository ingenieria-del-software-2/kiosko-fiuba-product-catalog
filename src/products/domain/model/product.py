"""Product entity module for the Product Catalog domain."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID, uuid4

from src.products.domain.model.value_objects import Money, ProductStatus


@dataclass(frozen=True)
class Product:
    """Product entity representing an item in the catalog."""

    name: str
    description: str
    price: Money
    category_id: UUID
    sku: str
    id: UUID = field(default_factory=uuid4)
    status: ProductStatus = ProductStatus.ACTIVE
    images: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def is_active(self) -> bool:
        """Check if product is active."""
        return self.status == ProductStatus.ACTIVE

    def has_tag(self, tag: str) -> bool:
        """Check if product has the specified tag."""
        return tag in self.tags
