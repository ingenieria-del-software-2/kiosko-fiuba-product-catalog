"""Product service for application layer."""

import uuid
from typing import List, Optional, Tuple

from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductFilterDTO,
    ProductResponseDTO,
    ProductUpdateDTO,
)
from src.products.domain.entities.product import Product
from src.products.domain.event_publisher.event_publisher import EventPublisher
from src.products.domain.repositories.category_repository import CategoryRepository
from src.products.domain.repositories.product_repository import ProductRepository


class ProductService:
    """Service for product operations."""

    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: Optional[CategoryRepository] = None,
        event_publisher: Optional[EventPublisher] = None,
    ) -> None:
        """Initialize service with repositories.

        Args:
            product_repository: Repository for product operations
            category_repository: Repository for category operations
            event_publisher: Event publisher for domain events
        """
        self._product_repository = product_repository
        self._category_repository = category_repository
        self._event_publisher = event_publisher

    async def create_product(
        self,
        product_data: ProductCreateDTO,
    ) -> ProductResponseDTO:
        """Create a new product.

        Args:
            product_data: DTO with product data

        Returns:
            DTO with created product data
        """
        product = await self._product_repository.create(product_data)

        # Publish event if event_publisher is provided
        if self._event_publisher:
            from src.products.domain.events.events import ProductCreatedEvent

            event = ProductCreatedEvent(
                event_id=uuid.uuid4(),
                event_type="product.created",
                aggregate_id=product.id,
                product_data={"product_id": str(product.id)},
            )
            await self._event_publisher.publish(event)

        return self._to_response_dto(product)

    async def get_product_by_id(
        self,
        product_id: uuid.UUID,
    ) -> Optional[ProductResponseDTO]:
        """Get a product by its ID.

        Args:
            product_id: Product ID

        Returns:
            DTO with product data or None if not found
        """
        product = await self._product_repository.get_by_id(product_id)

        if not product:
            return None

        return self._to_response_dto(product)

    async def get_product_by_sku(self, sku: str) -> Optional[ProductResponseDTO]:
        """Get a product by its SKU.

        Args:
            sku: Product SKU

        Returns:
            DTO with product data or None if not found
        """
        product = await self._product_repository.get_by_sku(sku)

        if not product:
            return None

        return self._to_response_dto(product)

    async def update_product(
        self,
        product_id: uuid.UUID,
        product_data: ProductUpdateDTO,
    ) -> Optional[ProductResponseDTO]:
        """Update a product.

        Args:
            product_id: Product ID
            product_data: DTO with updated product data

        Returns:
            DTO with updated product data or None if not found
        """
        product = await self._product_repository.update(product_id, product_data)

        if not product:
            return None

        return self._to_response_dto(product)

    async def delete_product(self, product_id: uuid.UUID) -> bool:
        """Delete a product.

        Args:
            product_id: Product ID

        Returns:
            True if deleted, False if not found
        """
        return await self._product_repository.delete(product_id)

    async def list_products(
        self,
        filters: Optional[ProductFilterDTO] = None,
    ) -> Tuple[List[ProductResponseDTO], int]:
        """List products with optional filtering.

        Args:
            filters: Optional filtering parameters

        Returns:
            List of DTOs with product data and total count
        """
        products, total = await self._product_repository.list(filters)
        return [self._to_response_dto(product) for product in products], total

    def _to_response_dto(self, product: Product) -> ProductResponseDTO:
        """Convert a Product entity to a ProductResponseDTO.

        Args:
            product: Product entity

        Returns:
            DTO with product data
        """
        # Convert to dictionary and then to DTO to handle nested structures
        product_dict = product.model_dump()
        return ProductResponseDTO(**product_dict)
