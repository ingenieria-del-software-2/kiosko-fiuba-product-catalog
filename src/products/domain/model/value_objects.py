"""Value objects for the Product Catalog domain."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class ProductStatus(str, Enum):
    """Status of a product in the catalog."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class InventoryStatus(str, Enum):
    """Status of a product in inventory."""

    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


@dataclass(frozen=True)
class Money:
    """Value object representing monetary values."""

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        """Validate money attributes."""
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency cannot be empty")
