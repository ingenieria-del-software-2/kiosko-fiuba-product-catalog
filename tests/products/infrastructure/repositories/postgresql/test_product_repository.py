"""Tests for the PostgreSQL product repository."""

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductFilterDTO,
    ProductUpdateDTO,
)
from src.products.domain.entities.product import Product
from src.products.infrastructure.repositories.postgresql.models import (
    ProductModel,
)
from src.products.infrastructure.repositories.postgresql.product_repository import (
    PostgreSQLProductRepository,
)


@pytest.fixture
def product_create_dto() -> ProductCreateDTO:
    """Product create DTO fixture."""
    return ProductCreateDTO(
        name="Test Product",
        slug="test-product",
        description="This is a test product",
        summary="Test product summary",
        price=Decimal("99.99"),
        currency="USD",
        sku="TEST-SKU-123",
        stock=100,
        category_ids=[uuid.uuid4()],
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


@pytest.fixture
def product_update_dto() -> ProductUpdateDTO:
    """Product update DTO fixture."""
    return ProductUpdateDTO(
        name="Updated Product",
        price=Decimal("129.99"),
    )


@pytest.mark.asyncio
async def test_create_product(
    db_session: AsyncSession,
    product_create_dto: ProductCreateDTO,
) -> None:
    """Test creating a product."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Create a product
    product = await repository.create(product_create_dto)

    # Verify the product
    assert isinstance(product, Product)
    assert product.name == product_create_dto.name
    assert product.slug == product_create_dto.slug
    assert float(product.price) == float(product_create_dto.price)
    assert product.sku == product_create_dto.sku

    # Verify it was saved to the database
    stmt = select(ProductModel).where(ProductModel.id == product.id)
    result = await db_session.execute(stmt)
    product_model = result.scalars().first()

    assert product_model is not None
    assert product_model.name == product_create_dto.name
    assert product_model.slug == product_create_dto.slug
    assert float(product_model.price_amount) == float(product_create_dto.price)
    assert product_model.sku == product_create_dto.sku


@pytest.mark.asyncio
async def test_get_product_by_id(
    db_session: AsyncSession,
    product_create_dto: ProductCreateDTO,
) -> None:
    """Test getting a product by ID."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Create a product
    created_product = await repository.create(product_create_dto)

    # Get the product by ID
    product = await repository.get_by_id(created_product.id)

    # Verify the product
    assert product is not None
    assert isinstance(product, Product)
    assert product.id == created_product.id
    assert product.name == product_create_dto.name
    assert product.slug == product_create_dto.slug
    assert float(product.price) == float(product_create_dto.price)
    assert product.sku == product_create_dto.sku


@pytest.mark.asyncio
async def test_get_product_by_id_not_found(
    db_session: AsyncSession,
) -> None:
    """Test getting a product by ID when it doesn't exist."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Get a non-existent product by ID
    product = await repository.get_by_id(uuid.uuid4())

    # Verify the result is None
    assert product is None


@pytest.mark.asyncio
async def test_get_product_by_sku(
    db_session: AsyncSession,
    product_create_dto: ProductCreateDTO,
) -> None:
    """Test getting a product by SKU."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Create a product
    created_product = await repository.create(product_create_dto)

    # Get the product by SKU
    product = await repository.get_by_sku(product_create_dto.sku)

    # Verify the product
    assert product is not None
    assert isinstance(product, Product)
    assert product.id == created_product.id
    assert product.name == product_create_dto.name
    assert product.slug == product_create_dto.slug
    assert float(product.price) == float(product_create_dto.price)
    assert product.sku == product_create_dto.sku


@pytest.mark.asyncio
async def test_get_product_by_sku_not_found(
    db_session: AsyncSession,
) -> None:
    """Test getting a product by SKU when it doesn't exist."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Get a non-existent product by SKU
    product = await repository.get_by_sku("NONEXISTENT-SKU")

    # Verify the result is None
    assert product is None


@pytest.mark.asyncio
async def test_update_product(
    db_session: AsyncSession,
    product_create_dto: ProductCreateDTO,
    product_update_dto: ProductUpdateDTO,
) -> None:
    """Test updating a product."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Create a product
    created_product = await repository.create(product_create_dto)

    # Update the product
    updated_product = await repository.update(created_product.id, product_update_dto)

    # Verify the updated product
    assert updated_product is not None
    assert isinstance(updated_product, Product)
    assert updated_product.id == created_product.id
    assert updated_product.name == product_update_dto.name
    assert float(updated_product.price) == float(product_update_dto.price)
    # Fields that weren't updated should remain the same
    assert updated_product.sku == product_create_dto.sku
    assert updated_product.slug == product_create_dto.slug

    # Verify it was updated in the database
    stmt = select(ProductModel).where(ProductModel.id == created_product.id)
    result = await db_session.execute(stmt)
    product_model = result.scalars().first()

    assert product_model is not None
    assert product_model.name == product_update_dto.name
    assert float(product_model.price_amount) == float(product_update_dto.price)
    assert product_model.sku == product_create_dto.sku
    assert product_model.slug == product_create_dto.slug


@pytest.mark.asyncio
async def test_update_product_not_found(
    db_session: AsyncSession,
    product_update_dto: ProductUpdateDTO,
) -> None:
    """Test updating a product when it doesn't exist."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Update a non-existent product
    updated_product = await repository.update(uuid.uuid4(), product_update_dto)

    # Verify the result is None
    assert updated_product is None


@pytest.mark.asyncio
async def test_delete_product(
    db_session: AsyncSession,
    product_create_dto: ProductCreateDTO,
) -> None:
    """Test deleting a product."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Create a product
    created_product = await repository.create(product_create_dto)

    # Delete the product
    deleted = await repository.delete(created_product.id)

    # Verify the result is True
    assert deleted is True

    # Verify it was deleted from the database
    stmt = select(ProductModel).where(ProductModel.id == created_product.id)
    result = await db_session.execute(stmt)
    product_model = result.scalars().first()

    assert product_model is None


@pytest.mark.asyncio
async def test_delete_product_not_found(
    db_session: AsyncSession,
) -> None:
    """Test deleting a product when it doesn't exist."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Delete a non-existent product
    deleted = await repository.delete(uuid.uuid4())

    # Verify the result is False
    assert deleted is False


@pytest.mark.asyncio
async def test_list_products(
    db_session: AsyncSession,
    product_create_dto: ProductCreateDTO,
) -> None:
    """Test listing products."""
    # Create repository
    repository = PostgreSQLProductRepository(db_session)

    # Create a product
    created_product = await repository.create(product_create_dto)

    # Verify the product was created successfully
    assert created_product is not None
    assert created_product.name == product_create_dto.name

    # Create a second product with different price
    second_dto = ProductCreateDTO(
        name="Second Product",
        slug="second-product",
        description="This is another test product",
        price=Decimal("149.99"),
        currency="USD",
        sku="TEST-SKU-456",
        tags=["test", "second"],
    )
    await repository.create(second_dto)

    # List all products
    filters = ProductFilterDTO()
    products, total = await repository.list(filters)

    # Verify results
    assert len(products) == 2
    assert total == 2
    assert all(isinstance(p, Product) for p in products)

    # Test filtering by price range
    price_filters = ProductFilterDTO(price_min=100.0, price_max=200.0)
    filtered_products, filtered_total = await repository.list(price_filters)

    # Verify filtered results
    assert len(filtered_products) == 1
    assert filtered_total == 1
    assert filtered_products[0].price > 100.0

    # Test pagination
    paginated_filters = ProductFilterDTO(limit=1, offset=0)
    paginated_products, paginated_total = await repository.list(paginated_filters)

    # Verify paginated results
    assert len(paginated_products) == 1
    assert paginated_total == 2
