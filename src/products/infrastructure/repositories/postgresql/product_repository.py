"""PostgreSQL implementation of ProductRepository."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.products.domain.model.product import Product
from src.products.domain.model.value_objects import Money, ProductStatus
from src.products.domain.repositories.product_repository import ProductRepository
from src.products.infrastructure.repositories.postgresql.models import ProductModel


class PostgresProductRepository(ProductRepository):
    """PostgreSQL implementation of the ProductRepository interface."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def create(self, product: Product) -> Product:
        """Create a new product in the database."""
        # Convert domain model to ORM model
        product_model = ProductModel(
            id=product.id,
            name=product.name,
            description=product.description,
            price_amount=product.price.amount,
            price_currency=product.price.currency,
            category_id=product.category_id,
            sku=product.sku,
            status=product.status.value,
            images=product.images,
            tags=product.tags,
            attributes=product.attributes,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

        # Add to session and commit
        self._session.add(product_model)
        await self._session.commit()
        await self._session.refresh(product_model)

        # Convert back to domain model and return
        return self._to_domain(product_model)

    async def update(self, product: Product) -> Product:
        """Update an existing product in the database."""
        # Fetch existing product
        query = select(ProductModel).where(ProductModel.id == product.id)
        result = await self._session.execute(query)
        product_model = result.scalar_one_or_none()

        if not product_model:
            raise ValueError(f"Product with ID {product.id} not found")

        # Update fields - using setattr to avoid type errors
        product_model.name = product.name
        product_model.description = product.description
        product_model.price_amount = product.price.amount
        product_model.price_currency = product.price.currency
        product_model.category_id = product.category_id
        product_model.sku = product.sku
        product_model.status = product.status.value
        product_model.images = product.images
        product_model.tags = product.tags
        product_model.attributes = product.attributes
        product_model.updated_at = product.updated_at

        # Commit changes
        await self._session.commit()
        await self._session.refresh(product_model)

        # Convert back to domain model and return
        return self._to_domain(product_model)

    async def delete(self, product_id: UUID) -> bool:
        """Delete a product from the database."""
        # Find product
        query = select(ProductModel).where(ProductModel.id == product_id)
        result = await self._session.execute(query)
        product_model = result.scalar_one_or_none()

        if not product_model:
            return False

        # Delete product
        await self._session.delete(product_model)
        await self._session.commit()

        return True

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Get a product by ID from the database."""
        query = select(ProductModel).where(ProductModel.id == product_id)
        result = await self._session.execute(query)
        product_model = result.scalar_one_or_none()

        if not product_model:
            return None

        return self._to_domain(product_model)

    async def list_products(self, limit: int = 100, offset: int = 0) -> List[Product]:
        """List products with pagination from the database."""
        query = (
            select(ProductModel)
            .order_by(ProductModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(query)
        product_models = result.scalars().all()

        return [self._to_domain(pm) for pm in product_models]

    async def search_products(
        self,
        query: str,
        category_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        """Search products by name, description or category."""
        # Build search query
        search_query = select(ProductModel)

        # Add text search condition
        if query:
            search_term = f"%{query}%"
            search_query = search_query.where(
                ProductModel.name.ilike(search_term)
                | ProductModel.description.ilike(search_term),
            )

        # Add category filter if provided
        if category_id:
            search_query = search_query.where(ProductModel.category_id == category_id)

        # Add pagination
        search_query = (
            search_query.order_by(
                ProductModel.created_at.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        # Execute query
        result = await self._session.execute(search_query)
        product_models = result.scalars().all()

        return [self._to_domain(pm) for pm in product_models]

    async def get_by_category(
        self,
        category_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        """Get products by category ID."""
        query = (
            select(ProductModel)
            .where(ProductModel.category_id == category_id)
            .order_by(ProductModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(query)
        product_models = result.scalars().all()

        return [self._to_domain(pm) for pm in product_models]

    def _to_domain(self, product_model: ProductModel) -> Product:
        """Convert ORM model to domain model."""
        # Cast to avoid type errors with SQLAlchemy descriptors
        id_val = cast(UUID, product_model.id)
        name_val = cast(str, product_model.name)
        description_val = cast(str, product_model.description)
        price_amount_val = cast(Decimal, product_model.price_amount)
        price_currency_val = cast(str, product_model.price_currency)
        category_id_val = cast(Optional[UUID], product_model.category_id)
        sku_val = cast(str, product_model.sku)
        status_val = cast(str, product_model.status)
        images_val = cast(List[str], product_model.images)
        tags_val = cast(List[str], product_model.tags)
        attributes_val = cast(Dict[str, Any], product_model.attributes)
        created_at_val = cast(datetime, product_model.created_at)
        updated_at_val = cast(datetime, product_model.updated_at)

        return Product(
            id=id_val,
            name=name_val,
            description=description_val,
            price=Money(
                amount=price_amount_val,
                currency=price_currency_val,
            ),
            category_id=category_id_val,
            sku=sku_val,
            status=ProductStatus(status_val),
            images=images_val,
            tags=tags_val,
            attributes=attributes_val,
            created_at=created_at_val,
            updated_at=updated_at_val,
        )
