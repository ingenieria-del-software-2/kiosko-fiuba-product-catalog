"""Test fixtures for the product catalog service."""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, AsyncGenerator, Dict, List
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.types import JSON

from src.api.app import get_app
from src.api.routes.products import router as product_router
from src.products.application.dtos.product_dtos import ProductResponseDTO
from src.shared.database.base import Base
from src.shared.database.dependencies import get_db_session
from src.shared.database.model_loader import load_all_models

# Patch PostgreSQL-specific ARRAY type with JSON for SQLite in tests
with patch("sqlalchemy.dialects.postgresql.ARRAY", lambda x: JSON):
    from src.products.infrastructure.repositories.postgresql.models import (
        CategoryModel,
        ProductModel,
    )


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    # Load models first
    load_all_models()

    # Make sure our patched models are loaded
    assert ProductModel.__tablename__ == "products"
    assert CategoryModel.__tablename__ == "categories"

    # Use SQLite for tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine
    finally:
        # Drop tables on cleanup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    return application


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test", timeout=2.0) as ac:
        yield ac


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Create a FastAPI app for testing."""
    app = FastAPI()
    app.include_router(product_router)
    return app


@pytest.fixture
def test_client(app: FastAPI) -> TestClient:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_product_service() -> AsyncMock:
    """Mock the product service."""
    with patch("src.api.routes.products.get_product_service") as mock:
        service_mock = AsyncMock()
        mock.return_value = service_mock
        yield service_mock


@pytest.fixture
def mock_category_service() -> AsyncMock:
    """Mock the category service."""
    with patch("src.api.routes.categories.get_category_service") as mock:
        service_mock = AsyncMock()
        mock.return_value = service_mock
        yield service_mock


@pytest.fixture
def sample_product_dto() -> ProductResponseDTO:
    """Create a sample product DTO."""
    return ProductResponseDTO(
        id=uuid.uuid4(),
        name="Sample Product",
        description="This is a sample product description",
        price=Decimal("99.99"),
        currency="USD",
        category_id=uuid.uuid4(),
        sku="SAMPLE-123",
        status="active",
        images=["https://example.com/sample.jpg"],
        tags=["sample", "test"],
        attributes={"color": "red", "size": "medium"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_product_list(
    sample_product_dto: ProductResponseDTO,
) -> List[ProductResponseDTO]:
    """Create a list of sample product DTOs."""
    # Create the first product based on sample_product_dto
    products = [sample_product_dto]

    # Add more products
    for i in range(1, 5):
        created_at = datetime.utcnow() - timedelta(days=i)
        products.append(
            ProductResponseDTO(
                id=uuid.uuid4(),
                name=f"Sample Product {i+1}",
                description=f"Description for sample product {i+1}",
                price=Decimal(f"{10.0 * (i+1):.2f}"),
                currency="USD",
                category_id=sample_product_dto.category_id,  # Same category
                sku=f"SAMPLE-{i+100}",
                status="active",
                images=[f"https://example.com/sample{i+1}.jpg"],
                tags=["sample"],
                attributes={"color": ["blue", "green", "yellow", "black"][i % 4]},
                created_at=created_at,
                updated_at=created_at,
            ),
        )
    return products


@pytest.fixture
def valid_product_create_data() -> Dict[str, Any]:
    """Valid data for creating a product."""
    return {
        "name": "New Product",
        "description": "Description for new product",
        "price": 49.99,
        "currency": "USD",
        "category_id": str(uuid.uuid4()),
        "sku": "NEW-SKU-001",
        "images": ["https://example.com/new.jpg"],
        "tags": ["new", "featured"],
        "attributes": {"color": "blue", "material": "cotton"},
    }


@pytest.fixture
def valid_product_update_data() -> Dict[str, Any]:
    """Valid data for updating a product."""
    return {
        "name": "Updated Product Name",
        "description": "Updated description",
        "price": 59.99,
    }


# Helper function to compare product DTOs with API responses
@pytest.fixture
def compare_product_dto_with_response() -> callable:
    """Helper function to compare product DTOs with API responses."""

    def _compare(dto: ProductResponseDTO, response_data: Dict[str, Any]) -> None:
        """Compare a product DTO with an API response."""
        assert str(dto.id) == response_data["id"]
        assert dto.name == response_data["name"]
        assert dto.description == response_data["description"]
        assert float(dto.price) == float(response_data["price"])
        assert dto.currency == response_data["currency"]
        assert str(dto.category_id) == response_data["category_id"]
        assert dto.sku == response_data["sku"]
        assert dto.status == response_data["status"]
        assert dto.images == response_data["images"]
        assert dto.tags == response_data["tags"]
        assert dto.attributes == response_data["attributes"]

    return _compare
