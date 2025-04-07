"""Tests for product routes."""

import uuid
from datetime import datetime
from typing import Any, Dict, List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.products.application.dtos.product_dtos import (
    AttributeDTO,
    ImageDTO,
    ProductFilterDTO,
    ProductResponseDTO,
)
from src.products.application.services.product_service import ProductService
from src.products.domain.exceptions.domain_exceptions import ProductNotFoundError


class MockProductService:
    """Mock product service for testing."""

    def __init__(self, sample_product: ProductResponseDTO) -> None:
        self.sample_product = sample_product

    async def create_product(self, product_data: Any) -> ProductResponseDTO:
        """Mock create product method."""
        return self.sample_product

    async def get_product_by_id(self, product_id: uuid.UUID) -> ProductResponseDTO:
        """Mock get product by ID method."""
        if str(product_id) == "00000000-0000-0000-0000-000000000000":
            raise ProductNotFoundError(product_id)
        return self.sample_product

    async def get_product_by_sku(self, sku: str) -> ProductResponseDTO:
        """Mock get product by SKU method."""
        if sku == "NONEXISTENT-SKU":
            return None
        return self.sample_product

    async def update_product(
        self,
        product_id: uuid.UUID,
        product_data: Any,
    ) -> ProductResponseDTO:
        """Mock update product method."""
        if str(product_id) == "00000000-0000-0000-0000-000000000000":
            raise ProductNotFoundError(product_id)
        return self.sample_product

    async def delete_product(self, product_id: uuid.UUID) -> bool:
        """Mock delete product method."""
        if str(product_id) == "00000000-0000-0000-0000-000000000000":
            raise ProductNotFoundError(product_id)
        return True

    async def get_products(self, filters: ProductFilterDTO) -> List[ProductResponseDTO]:
        """Mock get products method."""
        return [self.sample_product]

    async def get_products_by_category(
        self,
        category_id: uuid.UUID,
    ) -> List[ProductResponseDTO]:
        """Mock get products by category method."""
        return [self.sample_product]

    async def list_products(
        self,
        filters: ProductFilterDTO,
    ) -> tuple[List[ProductResponseDTO], int]:
        """Mock list products method."""
        return [self.sample_product], 1


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
            },
        ],
        "attributes": [
            {
                "name": "color",
                "value": "blue",
                "displayValue": "Blue",
                "isHighlighted": True,
            },
        ],
        "hasVariants": False,
        "highlightedFeatures": ["New Feature 1", "New Feature 2"],
    }


@pytest.fixture
def mock_product_service(sample_product_dto: ProductResponseDTO) -> ProductService:
    """Create a mock product service."""
    return MockProductService(sample_product_dto)


@pytest.fixture
def app(mock_product_service: ProductService) -> FastAPI:
    """Create a test FastAPI app with mocked dependencies."""
    from src.api.app import get_app

    app = get_app()

    from src.api.routes.products import get_product_service

    app.dependency_overrides[get_product_service] = lambda: mock_product_service

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client with mocked dependencies."""
    return TestClient(app)


def test_create_product_success(
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


def test_list_products(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
) -> None:
    """Test listing products with pagination."""
    response = client.get("/api/products?limit=10&offset=0")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 1  # We're mocking a list with a single product
    assert data["items"][0]["name"] == sample_product_dto.name


def test_get_products_by_category(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
) -> None:
    """Test getting products by category."""
    category_id = "92a1bf8a-cf99-4587-8afd-5df15be80352"  # Use a fixed UUID for testing
    response = client.get(f"/api/products?category_id={category_id}")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 1  # We're mocking a list with a single product
    assert data["items"][0]["name"] == sample_product_dto.name


def test_get_product_success(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
) -> None:
    """Test successfully getting a product by ID."""
    product_id = str(sample_product_dto.id)
    response = client.get(f"/api/products/{product_id}")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_product_dto.name
    assert float(data["price"]) == float(sample_product_dto.price)


def test_get_product_not_found(
    client: TestClient,
) -> None:
    """Test getting a non-existent product."""
    product_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/products/{product_id}")

    # Verify the response
    assert response.status_code == 404


@pytest.fixture
def sample_product_update_request() -> Dict[str, Any]:
    """Create a sample product update request for testing."""
    return {"name": "Updated Test Product", "price": 149.99}


def test_update_product_success(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
    sample_product_update_request: Dict[str, Any],
) -> None:
    """Test successfully updating a product."""
    product_id = str(sample_product_dto.id)
    response = client.put(
        f"/api/products/{product_id}",
        json=sample_product_update_request,
    )

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_product_dto.name
    assert float(data["price"]) == float(sample_product_dto.price)


def test_update_product_not_found(
    client: TestClient,
    sample_product_update_request: Dict[str, Any],
) -> None:
    """Test updating a non-existent product."""
    product_id = "00000000-0000-0000-0000-000000000000"
    response = client.put(
        f"/api/products/{product_id}",
        json=sample_product_update_request,
    )

    # Verify the response
    assert response.status_code == 404


def test_delete_product_success(
    client: TestClient,
    sample_product_dto: ProductResponseDTO,
) -> None:
    """Test successfully deleting a product."""
    product_id = str(sample_product_dto.id)
    response = client.delete(f"/api/products/{product_id}")

    # Verify the response
    assert response.status_code == 204
    assert response.content == b""  # No content


def test_delete_product_not_found(
    client: TestClient,
) -> None:
    """Test deleting a non-existent product."""
    product_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/api/products/{product_id}")

    # Verify the response
    assert response.status_code == 404
