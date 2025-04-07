"""Product application service."""

import uuid
from typing import List, Optional
from uuid import UUID

from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductResponseDTO,
    ProductUpdateDTO,
)
from src.products.domain.event_publisher.event_publisher import EventPublisher
from src.products.domain.events.events import (
    ProductCreatedEvent,
    ProductDeletedEvent,
    ProductUpdatedEvent,
)
from src.products.domain.exceptions.domain_exceptions import (
    CategoryNotFoundError,
    ProductNotFoundError,
)
from src.products.domain.model.product import Product
from src.products.domain.model.value_objects import Money, ProductStatus
from src.products.domain.repositories.category_repository import CategoryRepository
from src.products.domain.repositories.product_repository import ProductRepository


class ProductService:
    """Application service for managing products."""

    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
        event_publisher: EventPublisher,
    ) -> None:
        """Initialize with required repositories and event publisher."""
        self._product_repository = product_repository
        self._category_repository = category_repository
        self._event_publisher = event_publisher

    async def create_product(self, product_dto: ProductCreateDTO) -> ProductResponseDTO:
        """Create a new product.

        Args:
            product_dto: Data for the new product

        Returns:
            A DTO with the created product data

        Raises:
            CategoryNotFoundError: If the specified category does not exist
        """
        # Validate that the category exists
        category = await self._category_repository.get_by_id(product_dto.category_id)
        if not category:
            raise CategoryNotFoundError(product_dto.category_id)

        # Create new product
        product = Product(
            name=product_dto.name,
            description=product_dto.description,
            price=Money(amount=product_dto.price, currency=product_dto.currency),
            category_id=product_dto.category_id,
            sku=product_dto.sku,
            images=product_dto.images,
            tags=product_dto.tags,
            attributes=product_dto.attributes,
        )

        # Save to repository
        created_product = await self._product_repository.create(product)

        # Publish event
        event = ProductCreatedEvent(
            event_id=uuid.uuid4(),
            event_type="product.created",
            aggregate_id=created_product.id,
            product_data={
                "id": str(created_product.id),
                "name": created_product.name,
                "price": created_product.price.amount,
                "category_id": str(created_product.category_id),
            },
        )
        await self._event_publisher.publish(event)

        # Return response DTO
        return self._product_to_dto(created_product)

    async def update_product(self, product_dto: ProductUpdateDTO) -> ProductResponseDTO:
        """Update an existing product.

        Args:
            product_dto: Data for updating the product

        Returns:
            A DTO with the updated product data

        Raises:
            ProductNotFoundError: If the product does not exist
            CategoryNotFoundError: If the specified category does not exist
        """
        # Fetch existing product
        product = await self._product_repository.get_by_id(product_dto.id)
        if not product:
            raise ProductNotFoundError(product_dto.id)

        # If category is being changed, validate it exists
        if product_dto.category_id and product_dto.category_id != product.category_id:
            category = await self._category_repository.get_by_id(
                product_dto.category_id,
            )
            if not category:
                raise CategoryNotFoundError(product_dto.category_id)

        # Prepare data for updated product
        new_name = product_dto.name if product_dto.name is not None else product.name
        new_description = (
            product_dto.description
            if product_dto.description is not None
            else product.description
        )
        new_price = (
            Money(
                amount=product_dto.price,
                currency=(
                    product_dto.currency
                    if product_dto.currency
                    else product.price.currency
                ),
            )
            if product_dto.price is not None
            else product.price
        )
        new_category_id = (
            product_dto.category_id
            if product_dto.category_id is not None
            else product.category_id
        )
        new_sku = product_dto.sku if product_dto.sku is not None else product.sku
        new_status = (
            ProductStatus(product_dto.status)
            if product_dto.status is not None
            else product.status
        )
        new_images = (
            product_dto.images if product_dto.images is not None else product.images
        )
        new_tags = product_dto.tags if product_dto.tags is not None else product.tags
        new_attributes = (
            product_dto.attributes
            if product_dto.attributes is not None
            else product.attributes
        )

        # Create updated product
        updated_product = Product(
            id=product.id,
            name=new_name,
            description=new_description,
            price=new_price,
            category_id=new_category_id,
            sku=new_sku,
            status=new_status,
            images=new_images,
            tags=new_tags,
            attributes=new_attributes,
            created_at=product.created_at,
        )

        # Save to repository
        result = await self._product_repository.update(updated_product)

        # Publish event
        event = ProductUpdatedEvent(
            event_id=uuid.uuid4(),
            event_type="product.updated",
            aggregate_id=result.id,
            product_data={
                "id": str(result.id),
                "name": result.name,
                "price": result.price.amount,
                "category_id": str(result.category_id),
            },
            previous_data={
                "name": product.name,
                "price": product.price.amount,
                "category_id": str(product.category_id),
            },
        )
        await self._event_publisher.publish(event)

        # Return response DTO
        return self._product_to_dto(result)

    async def delete_product(self, product_id: UUID) -> bool:
        """Delete a product.

        Args:
            product_id: ID of the product to delete

        Returns:
            True if successful, False otherwise

        Raises:
            ProductNotFoundError: If the product does not exist
        """
        # Fetch existing product
        product = await self._product_repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)

        # Delete from repository
        result = await self._product_repository.delete(product_id)

        # Publish event
        if result:
            event = ProductDeletedEvent(
                event_id=uuid.uuid4(),
                event_type="product.deleted",
                aggregate_id=product_id,
                product_data={
                    "id": str(product.id),
                    "name": product.name,
                },
            )
            await self._event_publisher.publish(event)

        return result

    async def get_product(self, product_id: UUID) -> Optional[ProductResponseDTO]:
        """Get a product by ID.

        Args:
            product_id: ID of the product to fetch

        Returns:
            A DTO with the product data or None if not found
        """
        product = await self._product_repository.get_by_id(product_id)
        if not product:
            return None
        return self._product_to_dto(product)

    async def list_products(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ProductResponseDTO]:
        """List products with pagination.

        Args:
            limit: Maximum number of products to return
            offset: Number of products to skip

        Returns:
            A list of product DTOs
        """
        products = await self._product_repository.list_products(limit, offset)
        return [self._product_to_dto(product) for product in products]

    async def search_products(
        self,
        query: str,
        category_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ProductResponseDTO]:
        """Search products by name, description or category.

        Args:
            query: Search query
            category_id: Optional category filter
            limit: Maximum number of products to return
            offset: Number of products to skip

        Returns:
            A list of matching product DTOs
        """
        products = await self._product_repository.search_products(
            query,
            category_id,
            limit,
            offset,
        )
        return [self._product_to_dto(product) for product in products]

    async def get_products_by_category(
        self,
        category_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ProductResponseDTO]:
        """Get products by category.

        Args:
            category_id: ID of the category to get products for
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            A list of product DTOs in the specified category
        """
        products = await self._product_repository.get_by_category(
            category_id,
            limit,
            offset,
        )
        return [self._product_to_dto(product) for product in products]

    def _product_to_dto(self, product: Product) -> ProductResponseDTO:
        """Convert a Product entity to a ProductResponseDTO.

        Args:
            product: The product entity to convert

        Returns:
            A DTO with the product data
        """
        return ProductResponseDTO(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price.amount,
            currency=product.price.currency,
            category_id=product.category_id,
            sku=product.sku,
            status=product.status.value,
            images=product.images,
            tags=product.tags,
            attributes=product.attributes,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
