"""Category entity module for the Product Catalog domain."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Category:
    """Category entity representing a product category in the catalog."""

    name: str
    id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def is_root_category(self) -> bool:
        """Check if this is a root category (no parent)."""
        return self.parent_id is None
