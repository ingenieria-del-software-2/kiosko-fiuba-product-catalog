"""Product service for application layer."""

import logging
import uuid
from typing import Dict, List, Optional, Tuple

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

logger = logging.getLogger(__name__)


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
        try:
            # Create product using repository
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

            # Convert to response DTO
            return self._to_response_dto(product)
        except Exception as e:
            logger.error(f"Error creating product: {e!s}", exc_info=True)
            raise

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
        try:
            product = await self._product_repository.get_by_id(product_id)
            if not product:
                return None
            return self._to_response_dto(product)
        except Exception as e:
            logger.error(
                f"Error getting product by ID {product_id}: {e!s}",
                exc_info=True,
            )
            raise

    async def get_product_by_sku(self, sku: str) -> Optional[ProductResponseDTO]:
        """Get a product by its SKU.

        Args:
            sku: Product SKU

        Returns:
            DTO with product data or None if not found
        """
        try:
            product = await self._product_repository.get_by_sku(sku)
            if not product:
                return None
            return self._to_response_dto(product)
        except Exception as e:
            logger.error(f"Error getting product by SKU {sku}: {e!s}", exc_info=True)
            raise

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
        try:
            product = await self._product_repository.update(product_id, product_data)
            if not product:
                return None
            return self._to_response_dto(product)
        except Exception as e:
            logger.error(
                f"Error updating product {product_id}: {e!s}",
                exc_info=True,
            )
            raise

    async def delete_product(self, product_id: uuid.UUID) -> bool:
        """Delete a product.

        Args:
            product_id: Product ID

        Returns:
            True if deleted, False if not found
        """
        try:
            return await self._product_repository.delete(product_id)
        except Exception as e:
            logger.error(
                f"Error deleting product {product_id}: {e!s}",
                exc_info=True,
            )
            raise

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
        try:
            products, total = await self._product_repository.list(filters)
            return [self._to_response_dto(product) for product in products], total
        except Exception as e:
            logger.error(f"Error listing products: {e!s}", exc_info=True)
            raise

    def _to_response_dto(self, product: Product) -> ProductResponseDTO:
        """Convert a Product entity to a ProductResponseDTO.

        Args:
            product: Product entity

        Returns:
            DTO with product data
        """
        # Convert to dictionary and prepare data
        product_dict = product.model_dump()

        # Process UUIDs and add missing IDs
        self._convert_product_uuids(product_dict)

        # Create the DTO with the processed dictionary
        try:
            return ProductResponseDTO(**product_dict)
        except Exception as e:
            logger.error(f"Error creating ProductResponseDTO: {e!s}", exc_info=True)
            return ProductResponseDTO(**product_dict)

    def _convert_product_uuids(self, data: Dict) -> None:
        """Convert UUIDs to strings in the product dictionary.

        Args:
            data: Product dictionary to process
        """
        # Convert product ID
        if isinstance(data.get("id"), uuid.UUID):
            data["id"] = str(data["id"])

        # Convert brand ID if present
        if data.get("brand") and isinstance(data["brand"].get("id"), uuid.UUID):
            data["brand"]["id"] = str(data["brand"]["id"])

        # Process categories
        if data.get("categories"):
            self._process_categories(data["categories"])

        # Process images
        if data.get("images"):
            self._process_images(data["images"])

        # Process variants
        if data.get("variants"):
            self._process_variants(data["variants"])

        # Process attributes
        if data.get("attributes"):
            self._process_attributes(data["attributes"])

        # Process config options
        if data.get("config_options"):
            self._process_config_options(data["config_options"])

    def _process_categories(self, categories: List[Dict]) -> None:
        """Process category UUIDs.

        Args:
            categories: List of category dictionaries
        """
        for category in categories:
            if isinstance(category.get("id"), uuid.UUID):
                category["id"] = str(category["id"])
            if isinstance(category.get("parentId"), uuid.UUID):
                category["parentId"] = str(category["parentId"])

    def _process_images(self, images: List[Dict]) -> None:
        """Process image UUIDs and ensure each image has an ID.

        Args:
            images: List of image dictionaries
        """
        for i, image in enumerate(images):
            # Convert existing ID if it's a UUID
            if isinstance(image.get("id"), uuid.UUID):
                image["id"] = str(image["id"])

            # If image doesn't have an ID, generate one
            if "id" not in image:
                # Use index as part of the ID to ensure uniqueness
                image["id"] = str(uuid.uuid4())

                # Log this addition for debugging
                logger.debug(
                    f"Added missing image ID: {image['id']} for image at index {i}",
                )

            # Ensure isMain is present
            if "isMain" not in image and "is_main" in image:
                image["isMain"] = image["is_main"]

    def _process_variants(self, variants: List[Dict]) -> None:
        """Process variant UUIDs and their nested structures.

        Args:
            variants: List of variant dictionaries
        """
        for variant in variants:
            if isinstance(variant.get("id"), uuid.UUID):
                variant["id"] = str(variant["id"])

            # Process variant images if present
            if variant.get("images"):
                self._process_images(variant["images"])

    def _process_attributes(self, attributes: List[Dict]) -> None:
        """Process attribute UUIDs and add missing IDs.

        Args:
            attributes: List of attribute dictionaries
        """
        for i, attr in enumerate(attributes):
            if isinstance(attr, dict):
                # Add ID if missing
                if "id" not in attr:
                    attr["id"] = f"attr_{i}_{uuid.uuid4()}"
                # Convert ID if it's a UUID
                elif isinstance(attr["id"], uuid.UUID):
                    attr["id"] = str(attr["id"])

    def _process_config_options(self, config_options: List[Dict]) -> None:
        """Process config option UUIDs.

        Args:
            config_options: List of config option dictionaries
        """
        for option in config_options:
            if isinstance(option.get("id"), uuid.UUID):
                option["id"] = str(option["id"])
