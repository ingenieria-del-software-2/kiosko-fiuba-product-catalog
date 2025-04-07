"""Test fixtures for the product catalog service."""

import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, AsyncGenerator, Dict, List
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.api.app import get_app
from src.api.routes.products import router as product_router
from src.products.application.dtos.product_dtos import ProductResponseDTO
from src.shared.database.base import Base
from src.shared.database.connection import get_session_factory
from src.shared.database.dependencies import get_db_session
from src.shared.database.model_loader import load_all_models

# We don't need to define our own anyio_backend fixture
# Let pytest-asyncio handle it with its defaults


@pytest_asyncio.fixture(scope="function")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    # Load models first
    load_all_models()

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


@pytest_asyncio.fixture(scope="function")
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
    session_maker = async_sessionmaker(
        bind=_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async with session_maker() as session, session.begin():
        yield session
        # Transaction will automatically roll back


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


@pytest_asyncio.fixture
async def client(
    fastapi_app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
        timeout=2.0,
    ) as ac:
        yield ac


@pytest.fixture
def app() -> FastAPI:
    """Create a FastAPI app for testing."""
    app = FastAPI()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        app.state.db_session_factory = get_session_factory()
        yield

    app.router.lifespan_context = lifespan
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


@pytest.fixture
def test_app() -> FastAPI:
    """Create a test instance of the FastAPI application."""
    return get_app()
