"""Tests for product routes."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.testclient import TestClient as StarletteTestClient

from src.api.routes.products import router
from src.products.application.dtos.product_dtos import (
    ProductResponseDTO,
    ImageDTO,
    AttributeDTO,
)
from src.products.domain.exceptions.domain_exceptions import (
    ProductNotFoundError,
)
from src.products.domain.model.value_objects import ProductStatus


# Create a sample product DTO for testing
@pytest.fixture
def sample_product_dto() -> ProductResponseDTO:
    """Create a sample product DTO for testing."""
    return ProductResponseDTO(
        id=uuid.uuid4(),
        name="Test Product",
        slug="test-product",
        description="This is a test product",
        summary="A brief test product summary",
        price=99.99,
        currency="USD",
        sku="TEST-SKU-123",
        stock=100,
        isAvailable=True,
        isNew=True,
        isRefurbished=False,
        condition="new",
        categories=[],
        tags=["test", "sample"],
        images=[
            ImageDTO(
                id="1",
                url="http://example.com/image1.jpg",
                alt="Test Image 1",
                isMain=True,
                order=0,
            ),
            ImageDTO(
                id="2",
                url="http://example.com/image2.jpg",
                alt="Test Image 2",
                isMain=False,
                order=1,
            ),
        ],
        attributes=[
            AttributeDTO(
                id="1",
                name="color",
                value="red",
                displayValue="Red",
                isHighlighted=True,
            ),
            AttributeDTO(
                id="2",
                name="size",
                value="medium",
                displayValue="Medium",
                isHighlighted=False,
            ),
        ],
        hasVariants=False,
        highlightedFeatures=["Feature 1", "Feature 2"],
        created_at=datetime(2025, 4, 7, 8, 24, 1, 343443),
        updated_at=datetime(2025, 4, 7, 8, 24, 1, 343445),
    )


@pytest.fixture
def sample_product_request() -> Dict[str, Any]:
    """Create a sample product request for testing."""
    return {
        "name": "New Test Product",
        "description": "This is a new test product",
        "summary": "A brief summary",
        "price": 129.99,
        "currency": "USD",
        "sku": "NEW-SKU-456",
        "stock": 50,
        "isAvailable": True,
        "isNew": True,
        "condition": "new",
        "category_ids": [str(uuid.uuid4())],
        "tags": ["new", "test"],
        "images": [
            {
                "url": "http://example.com/new1.jpg",
                "alt": "New Image 1",
                "isMain": True,
                "order": 0,
            }
        ],
        "attributes": [
            {
                "name": "color",
                "value": "blue",
                "displayValue": "Blue",
                "isHighlighted": True,
            }
        ],
        "hasVariants": False,
        "highlightedFeatures": ["New Feature 1", "New Feature 2"],
    }


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client with mocked dependencies."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_create_product_success(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
    sample_product_request: Dict[str, Any],
) -> None:
    """Test successfully creating a product."""
    response = client.post("/api/products", json=sample_product_request)

    # Verify the response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_product_dto.name
    assert float(data["price"]) == float(sample_product_dto.price)


@pytest.mark.asyncio
async def test_list_products(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
) -> None:
    """Test listing products with pagination."""
    response = client.get("/api/products?limit=10&offset=0")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # We're mocking a list with a single product
    assert data[0]["name"] == sample_product_dto.name


@pytest.mark.asyncio
async def test_get_products_by_category(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
) -> None:
    """Test getting products by category."""
    category_id = "92a1bf8a-cf99-4587-8afd-5df15be80352"  # Use a fixed UUID for testing
    response = client.get(f"/api/products/category/{category_id}")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # We're mocking a list with a single product
    assert data[0]["name"] == sample_product_dto.name


@pytest.mark.asyncio
async def test_get_product_success(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
) -> None:
    """Test successfully getting a product by ID."""
    product_id = str(sample_product_dto.id)
    response = client.get(f"/api/products/{product_id}")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == sample_product_dto.name
    assert float(data["price"]) == float(sample_product_dto.price)


@pytest.mark.asyncio
async def test_get_product_not_found(
    client: TestClient,
    mock_product_service: Any,
) -> None:
    """Test getting a non-existent product."""
    # Setup the mock to raise a not found error
    product_id = "00000000-0000-0000-0000-000000000000"
    mock_product_service.get_product_by_id.side_effect = Exception(
        f"Product with ID {product_id} not found"
    )

    # Send the request
    response = client.get(f"/api/products/{product_id}")

    # Verify the response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.fixture
def sample_product_update_request() -> Dict[str, Any]:
    """Create a sample product update request."""
    return {"name": "Updated Product", "price": 149.99}


@pytest.mark.asyncio
async def test_update_product_success(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
    sample_product_update_request: Dict[str, Any],
) -> None:
    """Test successfully updating a product."""
    product_id = str(sample_product_dto.id)
    response = client.put(
        f"/api/products/{product_id}", json=sample_product_update_request
    )

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == sample_product_dto.name  # Using the mock return value


@pytest.mark.asyncio
async def test_update_product_not_found(
    client: TestClient,
    sample_product_update_request: Dict[str, Any],
    mock_product_service: Any,
) -> None:
    """Test updating a non-existent product."""
    # Setup the mock to raise a not found error
    product_id = "00000000-0000-0000-0000-000000000000"
    mock_product_service.update_product.side_effect = Exception(
        f"Product with ID {product_id} not found"
    )

    # Send the request
    response = client.put(
        f"/api/products/{product_id}", json=sample_product_update_request
    )

    # Verify the response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_delete_product_success(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
) -> None:
    """Test successfully deleting a product."""
    product_id = str(sample_product_dto.id)
    response = client.delete(f"/api/products/{product_id}")

    # Verify the response
    assert response.status_code == 204
    assert response.content == b""  # No content for successful delete


@pytest.mark.asyncio
async def test_delete_product_not_found(
    client: TestClient,
    mock_product_service: Any,
) -> None:
    """Test deleting a non-existent product."""
    # Setup the mock to raise a not found error
    product_id = "00000000-0000-0000-0000-000000000000"
    mock_product_service.delete_product.side_effect = Exception(
        f"Product with ID {product_id} not found"
    )

    # Send the request
    response = client.delete(f"/api/products/{product_id}")

    # Verify the response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()
