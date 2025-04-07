"""Domain exceptions for the Product Catalog domain."""

from uuid import UUID


class ProductNotFoundError(Exception):
    """Raised when a product is not found."""

    def __init__(self, product_id: UUID) -> None:
        """Initialize with product ID."""
        self.product_id = product_id
        super().__init__(f"Product with ID {product_id} not found")


class CategoryNotFoundError(Exception):
    """Raised when a category is not found."""

    def __init__(self, category_id: UUID) -> None:
        """Initialize with category ID."""
        self.category_id = category_id
        super().__init__(f"Category with ID {category_id} not found")


class InventoryNotFoundError(Exception):
    """Raised when inventory for a product is not found."""

    def __init__(self, product_id: UUID) -> None:
        """Initialize with product ID."""
        self.product_id = product_id
        super().__init__(f"Inventory for product with ID {product_id} not found")


class InsufficientInventoryError(Exception):
    """Raised when there is insufficient inventory for a product."""

    def __init__(self, product_id: UUID, requested: int, available: int) -> None:
        """Initialize with product ID, requested and available quantities."""
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient inventory for product {product_id}. "
            f"Requested: {requested}, Available: {available}",
        )
