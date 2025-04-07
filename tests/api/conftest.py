"""Configuration for tests."""

import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.testclient import TestClient

from src.api.dependencies import (
    get_category_repository,
    get_event_publisher,
    get_product_repository,
    get_product_service,
)
from src.products.application.dtos.product_dtos import ProductResponseDTO
from src.products.domain.repositories.category_repository import CategoryRepository
from src.products.domain.repositories.product_repository import ProductRepository
from src.shared.database.dependencies import get_db_session


@pytest.fixture
def mock_product_repository(sample_product_dto: ProductResponseDTO) -> AsyncMock:
    """Create a mock product repository."""
    mock = AsyncMock(spec=ProductRepository)
    # Set up specific return values for repository methods
    mock.create.return_value = sample_product_dto
    mock.get_by_id.return_value = sample_product_dto
    mock.get_by_sku.return_value = sample_product_dto
    mock.update.return_value = sample_product_dto
    mock.delete.return_value = True
    mock.list.return_value = ([sample_product_dto], 1)

    # Handle specific method that expects scalars().all()
    execute_mock = AsyncMock()
    scalars_mock = MagicMock()
    all_mock = MagicMock()

    all_mock.return_value = []  # Empty list of categories
    scalars_mock.return_value = all_mock
    execute_mock.return_value = scalars_mock
    
    # Use setattr to avoid direct private member access warnings
    session_mock = AsyncMock()
    session_mock.execute = execute_mock
    setattr(mock, "_session", session_mock)

    return mock


@pytest.fixture
def mock_category_repository() -> AsyncMock:
    """Create a mock category repository."""
    return AsyncMock(spec=CategoryRepository)


@pytest.fixture
def mock_event_publisher() -> AsyncMock:
    """Create a mock event publisher."""
    return AsyncMock()


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Create a mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_product_data() -> Dict:
    """Get sample product data."""
    return {
        "id": uuid.uuid4(),
        "name": "Test Product",
        "slug": "test-product",
        "description": "This is a test product",
        "summary": "Test product summary",
        "price": 99.99,
        "currency": "USD",
        "sku": "TEST-123",
        "stock": 100,
        "isAvailable": True,
        "isNew": True,
        "isRefurbished": False,
        "condition": "new",
        "tags": ["test", "product"],
        "categories": [],
        "images": [],
        "attributes": [],
        "highlightedFeatures": ["Feature 1", "Feature 2"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_product_dto() -> ProductResponseDTO:
    """Create a sample product DTO for testing."""
    return ProductResponseDTO(
        id=uuid.UUID("2ecd998f-0af0-41ee-82f5-ab4d09808e8f"),
        name="Test Product",
        slug="test-product",
        description="This is a test product",
        summary="Test product summary",
        price=99.99,
        currency="USD",
        sku="TEST-SKU-123",
        stock=100,
        isAvailable=True,
        isNew=True,
        isRefurbished=False,
        condition="new",
        tags=["test", "product"],
        categories=[],
        images=[],
        attributes=[
            {
                "name": "color",
                "value": "blue",
                "displayValue": "Blue",
                "isHighlighted": True,
            },
        ],
        highlightedFeatures=["Feature 1", "Feature 2"],
        created_at=datetime(2025, 4, 7, 8, 24, 1, 343443),
        updated_at=datetime(2025, 4, 7, 8, 24, 1, 343445),
    )


@pytest.fixture
def sample_product_request() -> Dict[str, Any]:
    """Create a sample product request for testing."""
    return {
        "name": "Test Product",
        "description": "This is a test product",
        "summary": "Test product summary",
        "price": 99.99,
        "currency": "USD",
        "sku": "TEST-SKU-123",
        "stock": 100,
        "isAvailable": True,
        "condition": "new",
        "tags": ["test", "product"],
        "category_ids": ["92a1bf8a-cf99-4587-8afd-5df15be80352"],
        "images": [
            {
                "url": "https://example.com/image1.jpg",
                "alt": "Test image 1",
                "isMain": True,
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
        "highlightedFeatures": ["Feature 1", "Feature 2"],
    }


@pytest.fixture
def mock_product_service(sample_product_dto: ProductResponseDTO) -> MagicMock:
    """Create a mock product service."""
    mock = MagicMock()
    mock.create_product = AsyncMock(return_value=sample_product_dto)
    mock.get_product_by_id = AsyncMock(return_value=sample_product_dto)
    mock.get_product_by_sku = AsyncMock(return_value=sample_product_dto)
    mock.update_product = AsyncMock(return_value=sample_product_dto)
    mock.delete_product = AsyncMock(return_value=True)
    mock.get_products = AsyncMock(return_value=[sample_product_dto])
    mock.get_products_by_category = AsyncMock(return_value=[sample_product_dto])
    return mock


@pytest.fixture
def override_app_dependencies(
    mock_product_repository: AsyncMock,
    mock_category_repository: AsyncMock,
    mock_event_publisher: AsyncMock,
    mock_db_session: AsyncMock,
    mock_product_service: MagicMock,
) -> Dict[Callable, Callable]:
    """Override app dependencies for testing."""

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db_session

    async def override_get_product_repository() -> ProductRepository:
        return cast(ProductRepository, mock_product_repository)

    async def override_get_category_repository() -> CategoryRepository:
        return cast(CategoryRepository, mock_category_repository)

    async def override_get_event_publisher() -> AsyncMock:
        return mock_event_publisher

    async def override_get_product_service() -> MagicMock:
        return mock_product_service

    return {
        get_db_session: override_get_db_session,
        get_product_repository: override_get_product_repository,
        get_category_repository: override_get_category_repository,
        get_event_publisher: override_get_event_publisher,
        get_product_service: override_get_product_service,
    }


@pytest.fixture
def app(override_app_dependencies: Dict) -> FastAPI:
    """Create a test app with overridden dependencies."""
    from src.api.app import get_app

    app = get_app()

    # Override dependencies
    for original, override in override_app_dependencies.items():
        app.dependency_overrides[original] = override

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(app)
