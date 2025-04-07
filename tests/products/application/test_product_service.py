"""Tests for the product service."""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductResponseDTO,
)
from src.products.application.services.product_service import ProductService
from src.products.domain.model.product import Product
from src.products.domain.model.value_objects import Money


@pytest.mark.asyncio
async def test_product_service_create() -> None:
    """Test the create_product method of the product service."""
    # Create mocks
    product_repo = AsyncMock()
    category_repo = AsyncMock()
    event_publisher = AsyncMock()

    # Setup the repository mocks
    product_id = uuid.uuid4()
    category_id = uuid.uuid4()

    # Category repository should return a category
    category_repo.get_by_id.return_value = MagicMock(id=category_id)

    # Product repository should return a Product object
    product = Product(
        id=product_id,
        name="Test Product",
        description="This is a test product",
        price=Money(amount=Decimal("99.99"), currency="USD"),
        category_id=category_id,
        sku="TEST-SKU-123",
        images=["http://example.com/image1.jpg"],
        tags=["test", "sample"],
        attributes={"color": "red", "size": "medium"},
    )
    product_repo.create.return_value = product

    # Create the service with mocks
    service = ProductService(
        product_repository=product_repo,
        category_repository=category_repo,
        event_publisher=event_publisher,
    )

    # Create a product DTO
    product_dto = ProductCreateDTO(
        name="Test Product",
        description="This is a test product",
        price=Decimal("99.99"),
        currency="USD",
        category_id=category_id,
        sku="TEST-SKU-123",
        images=["http://example.com/image1.jpg"],
        tags=["test", "sample"],
        attributes={"color": "red", "size": "medium"},
    )

    # Call the service method
    result = await service.create_product(product_dto)

    # Verify the result is a ProductResponseDTO
    assert isinstance(result, ProductResponseDTO)
    assert result.id == product_id
    assert result.name == product_dto.name
    assert result.price == product_dto.price

    # Verify the repository was called
    product_repo.create.assert_called_once()

    # Verify the event publisher was called
    event_publisher.publish.assert_called_once()
