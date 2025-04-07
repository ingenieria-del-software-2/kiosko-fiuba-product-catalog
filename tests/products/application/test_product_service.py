"""Tests for the product service."""

import uuid
from decimal import Decimal
from typing import (
    Any,
    Optional,
    Tuple,
)
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductFilterDTO,
    ProductResponseDTO,
    ProductUpdateDTO,
)
from src.products.application.services.product_service import ProductService
from src.products.domain.entities.product import Product


@pytest.fixture
def product_id() -> uuid.UUID:
    """Product ID fixture."""
    return uuid.uuid4()


@pytest.fixture
def category_id() -> uuid.UUID:
    """Category ID fixture."""
    return uuid.uuid4()


@pytest.fixture
def sample_product(product_id: uuid.UUID) -> Product:
    """Sample product fixture."""
    return Product(
        id=product_id,
        name="Test Product",
        slug="test-product",
        description="This is a test product",
        price=99.99,
        currency="USD",
        sku="TEST-SKU-123",
        images=[
            {
                "id": "img1",
                "url": "http://example.com/image1.jpg",
                "alt": "Test Image 1",
                "isMain": True,
                "order": 0,
            },
        ],
        tags=["test", "sample"],
        attributes=[
            {
                "id": "attr1",
                "name": "color",
                "value": "red",
                "displayValue": "Red",
                "isHighlighted": False,
            },
            {
                "id": "attr2",
                "name": "size",
                "value": "medium",
                "displayValue": "Medium",
                "isHighlighted": False,
            },
        ],
    )


@pytest.fixture
def mocked_repos(
    product_id: uuid.UUID,
    category_id: uuid.UUID,
    sample_product: Product,
) -> Tuple[AsyncMock, AsyncMock, AsyncMock]:
    """Create mocked repositories for testing."""
    product_repo = AsyncMock()
    category_repo = AsyncMock()
    event_publisher = AsyncMock()

    # Setup mocks
    product_repo.create.return_value = sample_product
    product_repo.get_by_id.return_value = sample_product
    product_repo.get_by_sku.return_value = sample_product
    product_repo.update.return_value = sample_product
    product_repo.delete.return_value = True
    product_repo.list.return_value = ([sample_product], 1)

    # Handle special cases for not found
    def get_by_id_side_effect(pid: uuid.UUID) -> Optional[Product]:
        if pid == uuid.UUID("00000000-0000-0000-0000-000000000000"):
            return None
        return sample_product

    product_repo.get_by_id.side_effect = get_by_id_side_effect

    def get_by_sku_side_effect(sku: str) -> Optional[Product]:
        if sku == "NONEXISTENT-SKU":
            return None
        return sample_product

    product_repo.get_by_sku.side_effect = get_by_sku_side_effect

    def update_side_effect(pid: uuid.UUID, data: Any) -> Optional[Product]:
        if pid == uuid.UUID("00000000-0000-0000-0000-000000000000"):
            return None
        return sample_product

    product_repo.update.side_effect = update_side_effect

    def delete_side_effect(pid: uuid.UUID) -> bool:
        return pid != uuid.UUID("00000000-0000-0000-0000-000000000000")

    product_repo.delete.side_effect = delete_side_effect

    # Category repo
    category_repo.get_by_id.return_value = MagicMock(id=category_id)

    return product_repo, category_repo, event_publisher


@pytest.fixture
def product_service(
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
) -> ProductService:
    """Create the product service with mocked dependencies."""
    product_repo, category_repo, event_publisher = mocked_repos
    return ProductService(
        product_repository=product_repo,
        category_repository=category_repo,
        event_publisher=event_publisher,
    )


@pytest.mark.asyncio
async def test_product_service_create(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
    category_id: uuid.UUID,
) -> None:
    """Test the create_product method of the product service."""
    product_repo, _, event_publisher = mocked_repos

    # Create a product DTO
    product_dto = ProductCreateDTO(
        name="Test Product",
        description="This is a test product",
        price=Decimal("99.99"),
        currency="USD",
        category_id=category_id,
        sku="TEST-SKU-123",
        images=[
            {
                "url": "http://example.com/image1.jpg",
                "alt": "Test Image 1",
                "isMain": True,
                "order": 0,
            },
        ],
        tags=["test", "sample"],
        attributes=[
            {
                "name": "color",
                "value": "red",
                "displayValue": "Red",
                "isHighlighted": False,
            },
            {
                "name": "size",
                "value": "medium",
                "displayValue": "Medium",
                "isHighlighted": False,
            },
        ],
    )

    # Call the service method
    result = await product_service.create_product(product_dto)

    # Verify the result is a ProductResponseDTO
    assert isinstance(result, ProductResponseDTO)
    assert result.name == product_dto.name
    assert result.price == product_dto.price

    # Verify the repository was called
    product_repo.create.assert_called_once()

    # Verify the event publisher was called
    event_publisher.publish.assert_called_once()


@pytest.mark.asyncio
async def test_get_product_by_id_success(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
    product_id: uuid.UUID,
) -> None:
    """Test getting a product by ID successfully."""
    product_repo, _, _ = mocked_repos

    # Call the service method
    result = await product_service.get_product_by_id(product_id)

    # Verify the result
    assert isinstance(result, ProductResponseDTO)
    assert result.id == product_id

    # Verify the repository was called
    product_repo.get_by_id.assert_called_once_with(product_id)


@pytest.mark.asyncio
async def test_get_product_by_id_not_found(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
) -> None:
    """Test getting a product by ID when it doesn't exist."""
    product_repo, _, _ = mocked_repos
    non_existent_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

    # Call the service method
    result = await product_service.get_product_by_id(non_existent_id)

    # Verify the result is None
    assert result is None

    # Verify the repository was called
    product_repo.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.asyncio
async def test_get_product_by_sku_success(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
) -> None:
    """Test getting a product by SKU successfully."""
    product_repo, _, _ = mocked_repos
    sku = "TEST-SKU-123"

    # Call the service method
    result = await product_service.get_product_by_sku(sku)

    # Verify the result
    assert isinstance(result, ProductResponseDTO)
    assert result.sku == sku

    # Verify the repository was called
    product_repo.get_by_sku.assert_called_once_with(sku)


@pytest.mark.asyncio
async def test_get_product_by_sku_not_found(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
) -> None:
    """Test getting a product by SKU when it doesn't exist."""
    product_repo, _, _ = mocked_repos
    non_existent_sku = "NONEXISTENT-SKU"

    # Call the service method
    result = await product_service.get_product_by_sku(non_existent_sku)

    # Verify the result is None
    assert result is None

    # Verify the repository was called
    product_repo.get_by_sku.assert_called_once_with(non_existent_sku)


@pytest.mark.asyncio
async def test_update_product_success(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
    product_id: uuid.UUID,
) -> None:
    """Test updating a product successfully."""
    product_repo, _, _ = mocked_repos

    # Create an update DTO
    update_dto = ProductUpdateDTO(
        name="Updated Product",
        price=Decimal("129.99"),
    )

    # Call the service method
    result = await product_service.update_product(product_id, update_dto)

    # Verify the result
    assert isinstance(result, ProductResponseDTO)

    # Verify the repository was called
    product_repo.update.assert_called_once_with(product_id, update_dto)


@pytest.mark.asyncio
async def test_update_product_not_found(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
) -> None:
    """Test updating a product when it doesn't exist."""
    product_repo, _, _ = mocked_repos
    non_existent_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

    # Create an update DTO
    update_dto = ProductUpdateDTO(
        name="Updated Product",
        price=Decimal("129.99"),
    )

    # Call the service method
    result = await product_service.update_product(non_existent_id, update_dto)

    # Verify the result is None
    assert result is None

    # Verify the repository was called
    product_repo.update.assert_called_once_with(non_existent_id, update_dto)


@pytest.mark.asyncio
async def test_delete_product_success(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
    product_id: uuid.UUID,
) -> None:
    """Test deleting a product successfully."""
    product_repo, _, _ = mocked_repos

    # Call the service method
    result = await product_service.delete_product(product_id)

    # Verify the result is True
    assert result is True

    # Verify the repository was called
    product_repo.delete.assert_called_once_with(product_id)


@pytest.mark.asyncio
async def test_delete_product_not_found(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
) -> None:
    """Test deleting a product when it doesn't exist."""
    product_repo, _, _ = mocked_repos
    non_existent_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

    # Call the service method
    result = await product_service.delete_product(non_existent_id)

    # Verify the result is False
    assert result is False

    # Verify the repository was called
    product_repo.delete.assert_called_once_with(non_existent_id)


@pytest.mark.asyncio
async def test_list_products(
    product_service: ProductService,
    mocked_repos: Tuple[AsyncMock, AsyncMock, AsyncMock],
) -> None:
    """Test listing products with filters."""
    product_repo, _, _ = mocked_repos

    # Create filter DTO
    filters = ProductFilterDTO(
        category_id=uuid.uuid4(),
        price_min=50.0,
        price_max=150.0,
        limit=10,
        offset=0,
    )

    # Call the service method
    products, total = await product_service.list_products(filters)

    # Verify the results
    assert len(products) == 1
    assert isinstance(products[0], ProductResponseDTO)
    assert total == 1

    # Verify the repository was called
    product_repo.list.assert_called_once_with(filters)
