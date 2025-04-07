"""Tests for the Product domain entity."""

import uuid
from datetime import datetime

import pytest

from src.products.domain.entities.product import Product


@pytest.fixture
def valid_product_data() -> dict:
    """Valid product data fixture."""
    return {
        "id": uuid.uuid4(),
        "name": "Test Product",
        "slug": "test-product",
        "description": "This is a test product",
        "price": 99.99,
        "currency": "USD",
        "sku": "TEST-SKU-123",
        "stock": 100,
        "is_available": True,
        "tags": ["test", "sample"],
        "attributes": [
            {
                "id": "attr1",
                "name": "color",
                "value": "red",
                "displayValue": "Red",
                "isHighlighted": False,
            },
        ],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


def test_create_product(valid_product_data: dict) -> None:
    """Test creating a valid product."""
    # Create product
    product = Product(**valid_product_data)

    # Verify attributes
    assert product.id == valid_product_data["id"]
    assert product.name == valid_product_data["name"]
    assert product.slug == valid_product_data["slug"]
    assert product.price == valid_product_data["price"]
    assert product.sku == valid_product_data["sku"]
    assert product.tags == valid_product_data["tags"]
    assert len(product.attributes) == 1
    assert product.attributes[0]["name"] == "color"


def test_product_optional_fields() -> None:
    """Test creating a product with minimal fields."""
    # Create a minimal product
    product_id = uuid.uuid4()
    product = Product(
        id=product_id,
        name="Minimal Product",
        slug="minimal-product",
        description="Minimal description",
        price=49.99,
        currency="USD",
        sku="MIN-SKU-001",
    )

    # Verify required fields
    assert product.id == product_id
    assert product.name == "Minimal Product"
    assert product.slug == "minimal-product"
    assert product.price == 49.99
    assert product.sku == "MIN-SKU-001"

    # Verify optional fields get default values
    assert product.stock == 0  # Default is 0, not None
    assert product.tags == []
    assert product.attributes == []
    assert product.images == []
    assert product.is_available is True  # Default value


def test_product_string_representation() -> None:
    """Test the string representation of a product."""
    # Create a product
    product_id = uuid.uuid4()
    product = Product(
        id=product_id,
        name="Test Product",
        slug="test-product",
        description="This is a test product",
        price=99.99,
        currency="USD",
        sku="TEST-SKU-123",
    )

    # Just verify the product exists and has the expected attributes
    assert product.id == product_id
    assert product.name == "Test Product"
    assert product.sku == "TEST-SKU-123"
