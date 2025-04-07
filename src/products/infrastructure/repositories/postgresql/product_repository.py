"""Implementation of a ProductRepository using PostgreSQL."""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductFilterDTO,
    ProductUpdateDTO,
)
from src.products.domain.entities.product import Product
from src.products.domain.repositories.product_repository import ProductRepository
from src.products.infrastructure.repositories.postgresql.models import (
    CategoryModel,
    ConfigOptionModel,
    ProductImageModel,
    ProductModel,
    ProductVariantModel,
    product_categories,
)


class PostgreSQLProductRepository(ProductRepository):
    """PostgreSQL implementation of ProductRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create(self, product_dto: ProductCreateDTO) -> Product:
        """Create a new product.

        Args:
            product_dto: DTO with product data

        Returns:
            Created product entity
        """
        # Create the product model
        product_model = ProductModel(
            name=product_dto.name,
            slug=product_dto.slug,
            description=product_dto.description,
            summary=product_dto.summary,
            price_amount=product_dto.price,
            price_currency=product_dto.currency,
            compare_at_price=product_dto.compareAtPrice,
            brand_id=product_dto.brand_id,
            model=product_dto.model,
            sku=product_dto.sku,
            stock=product_dto.stock,
            is_available=product_dto.isAvailable,
            is_new=product_dto.isNew,
            is_refurbished=product_dto.isRefurbished,
            condition=product_dto.condition,
            has_variants=product_dto.hasVariants,
            tags=product_dto.tags,
            attributes=product_dto.attributes,
            highlighted_features=product_dto.highlightedFeatures,
            shipping=product_dto.shipping,
            warranty=product_dto.warranty,
        )

        self._session.add(product_model)

        # Add categories
        if product_dto.category_ids:
            stmt = select(CategoryModel).where(
                CategoryModel.id.in_(product_dto.category_ids),
            )
            categories = (await self._session.execute(stmt)).scalars().all()
            product_model.categories = categories

        # Add images
        if product_dto.images:
            for image_data in product_dto.images:
                image = ProductImageModel(
                    product_id=product_model.id,
                    url=image_data["url"],
                    alt=image_data.get("alt"),
                    is_main=image_data.get("isMain", False),
                    order=image_data.get("order", 0),
                )
                self._session.add(image)

        # Add variants
        if product_dto.variants:
            for variant_data in product_dto.variants:
                variant = ProductVariantModel(
                    parent_product_id=product_model.id,
                    name=variant_data["name"],
                    sku=variant_data["sku"],
                    price_amount=variant_data["price"],
                    price_currency=product_dto.currency,
                    compare_at_price=variant_data.get("compareAtPrice"),
                    stock=variant_data.get("stock", 0),
                    is_available=variant_data.get("isAvailable", True),
                    is_selected=variant_data.get("isSelected", False),
                    attributes=variant_data.get("attributes", {}),
                )
                self._session.add(variant)

                # Add variant images if they exist
                if variant_data.get("images"):
                    for v_image_data in variant_data["images"]:
                        v_image = ProductImageModel(
                            product_id=product_model.id,
                            url=v_image_data["url"],
                            alt=v_image_data.get("alt"),
                            is_main=v_image_data.get("isMain", False),
                            order=v_image_data.get("order", 0),
                        )
                        self._session.add(v_image)

        # Add config options
        if product_dto.configOptions:
            for config_data in product_dto.configOptions:
                config = ConfigOptionModel(
                    product_id=product_model.id,
                    name=config_data["name"],
                    values=config_data["values"],
                )
                self._session.add(config)

        await self._session.flush()

        # Convert to domain entity
        return await self._to_domain_entity(product_model)

    async def get_by_id(self, product_id: uuid.UUID) -> Optional[Product]:
        """Get a product by its ID.

        Args:
            product_id: Product ID

        Returns:
            Product entity or None if not found
        """
        stmt = (
            select(ProductModel)
            .options(
                selectinload(ProductModel.categories),
                selectinload(ProductModel.images),
                selectinload(ProductModel.variants),
                selectinload(ProductModel.config_options),
                selectinload(ProductModel.reviews),
                joinedload(ProductModel.brand),
            )
            .where(ProductModel.id == product_id)
        )

        result = await self._session.execute(stmt)
        product_model = result.scalars().first()

        if not product_model:
            return None

        return await self._to_domain_entity(product_model)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by its SKU.

        Args:
            sku: Product SKU

        Returns:
            Product entity or None if not found
        """
        stmt = (
            select(ProductModel)
            .options(
                selectinload(ProductModel.categories),
                selectinload(ProductModel.images),
                selectinload(ProductModel.variants),
                selectinload(ProductModel.config_options),
                selectinload(ProductModel.reviews),
                joinedload(ProductModel.brand),
            )
            .where(ProductModel.sku == sku)
        )

        result = await self._session.execute(stmt)
        product_model = result.scalars().first()

        if not product_model:
            return None

        return await self._to_domain_entity(product_model)

    async def update(
        self,
        product_id: uuid.UUID,
        product_dto: ProductUpdateDTO,
    ) -> Optional[Product]:
        """Update a product.

        Args:
            product_id: Product ID
            product_dto: DTO with updated product data

        Returns:
            Updated product entity or None if not found
        """
        stmt = (
            select(ProductModel)
            .options(
                selectinload(ProductModel.categories),
                selectinload(ProductModel.images),
                selectinload(ProductModel.variants),
                selectinload(ProductModel.config_options),
            )
            .where(ProductModel.id == product_id)
        )

        result = await self._session.execute(stmt)
        product_model = result.scalars().first()

        if not product_model:
            return None

        # Update product fields
        if product_dto.name is not None:
            product_model.name = product_dto.name
        if product_dto.slug is not None:
            product_model.slug = product_dto.slug
        if product_dto.description is not None:
            product_model.description = product_dto.description
        if product_dto.summary is not None:
            product_model.summary = product_dto.summary
        if product_dto.price is not None:
            product_model.price_amount = product_dto.price
        if product_dto.compareAtPrice is not None:
            product_model.compare_at_price = product_dto.compareAtPrice
        if product_dto.currency is not None:
            product_model.price_currency = product_dto.currency
        if product_dto.brand_id is not None:
            product_model.brand_id = product_dto.brand_id
        if product_dto.model is not None:
            product_model.model = product_dto.model
        if product_dto.sku is not None:
            product_model.sku = product_dto.sku
        if product_dto.stock is not None:
            product_model.stock = product_dto.stock
        if product_dto.isAvailable is not None:
            product_model.is_available = product_dto.isAvailable
        if product_dto.isNew is not None:
            product_model.is_new = product_dto.isNew
        if product_dto.isRefurbished is not None:
            product_model.is_refurbished = product_dto.isRefurbished
        if product_dto.condition is not None:
            product_model.condition = product_dto.condition
        if product_dto.hasVariants is not None:
            product_model.has_variants = product_dto.hasVariants
        if product_dto.tags is not None:
            product_model.tags = product_dto.tags
        if product_dto.attributes is not None:
            product_model.attributes = product_dto.attributes
        if product_dto.highlightedFeatures is not None:
            product_model.highlighted_features = product_dto.highlightedFeatures
        if product_dto.shipping is not None:
            product_model.shipping = product_dto.shipping
        if product_dto.warranty is not None:
            product_model.warranty = product_dto.warranty

        # Update categories if provided
        if product_dto.category_ids is not None:
            # Clear existing categories
            product_model.categories = []

            if product_dto.category_ids:
                stmt = select(CategoryModel).where(
                    CategoryModel.id.in_(product_dto.category_ids),
                )
                categories = (await self._session.execute(stmt)).scalars().all()
                product_model.categories = categories

        # Update images if provided
        if product_dto.images is not None:
            # Delete existing images
            delete_stmt = select(ProductImageModel).where(
                ProductImageModel.product_id == product_id,
            )
            existing_images = (await self._session.execute(delete_stmt)).scalars().all()
            for image in existing_images:
                await self._session.delete(image)

            # Add new images
            for image_data in product_dto.images:
                image = ProductImageModel(
                    product_id=product_model.id,
                    url=image_data["url"],
                    alt=image_data.get("alt"),
                    is_main=image_data.get("isMain", False),
                    order=image_data.get("order", 0),
                )
                self._session.add(image)

        # Update variants if provided
        if product_dto.variants is not None:
            # Delete existing variants
            delete_stmt = select(ProductVariantModel).where(
                ProductVariantModel.parent_product_id == product_id,
            )
            existing_variants = (
                (await self._session.execute(delete_stmt)).scalars().all()
            )
            for variant in existing_variants:
                await self._session.delete(variant)

            # Add new variants
            for variant_data in product_dto.variants:
                variant = ProductVariantModel(
                    parent_product_id=product_model.id,
                    name=variant_data["name"],
                    sku=variant_data["sku"],
                    price_amount=variant_data["price"],
                    price_currency=product_model.price_currency,
                    compare_at_price=variant_data.get("compareAtPrice"),
                    stock=variant_data.get("stock", 0),
                    is_available=variant_data.get("isAvailable", True),
                    is_selected=variant_data.get("isSelected", False),
                    attributes=variant_data.get("attributes", {}),
                )
                self._session.add(variant)

        # Update config options if provided
        if product_dto.configOptions is not None:
            # Delete existing config options
            delete_stmt = select(ConfigOptionModel).where(
                ConfigOptionModel.product_id == product_id,
            )
            existing_configs = (
                (await self._session.execute(delete_stmt)).scalars().all()
            )
            for config in existing_configs:
                await self._session.delete(config)

            # Add new config options
            for config_data in product_dto.configOptions:
                config = ConfigOptionModel(
                    product_id=product_model.id,
                    name=config_data["name"],
                    values=config_data["values"],
                )
                self._session.add(config)

        # Update timestamp
        product_model.updated_at = datetime.utcnow()

        await self._session.flush()

        # Convert to domain entity
        return await self._to_domain_entity(product_model)

    async def delete(self, product_id: uuid.UUID) -> bool:
        """Delete a product.

        Args:
            product_id: Product ID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        result = await self._session.execute(stmt)
        product_model = result.scalars().first()

        if not product_model:
            return False

        await self._session.delete(product_model)
        await self._session.flush()

        return True

    async def list(
        self,
        filters: Optional[ProductFilterDTO] = None,
    ) -> Tuple[List[Product], int]:
        """List products with optional filtering.

        Args:
            filters: Optional filtering parameters

        Returns:
            List of product entities and total count
        """
        filters = filters or ProductFilterDTO()

        # Base query for data
        query = select(ProductModel).options(
            selectinload(ProductModel.categories),
            selectinload(ProductModel.images),
            joinedload(ProductModel.brand),
        )

        # Base query for count
        count_query = select(func.count()).select_from(ProductModel)

        # Apply filters
        conditions = []

        if filters.category_id:
            conditions.append(
                ProductModel.id.in_(
                    select(product_categories.c.product_id)
                    .where(product_categories.c.category_id == filters.category_id)
                    .scalar_subquery(),
                ),
            )

        if filters.brand_id:
            conditions.append(ProductModel.brand_id == filters.brand_id)

        if filters.price_min is not None:
            conditions.append(ProductModel.price_amount >= filters.price_min)

        if filters.price_max is not None:
            conditions.append(ProductModel.price_amount <= filters.price_max)

        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    ProductModel.name.ilike(search_term),
                    ProductModel.description.ilike(search_term),
                    ProductModel.sku.ilike(search_term),
                ),
            )

        if filters.tags:
            for tag in filters.tags:
                # For PostgreSQL's JSON array containment
                conditions.append(ProductModel.tags.contains([tag]))

        if filters.is_available is not None:
            conditions.append(ProductModel.is_available == filters.is_available)

        if filters.is_new is not None:
            conditions.append(ProductModel.is_new == filters.is_new)

        if filters.condition:
            conditions.append(ProductModel.condition == filters.condition)

        # Add conditions to queries
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Apply sorting
        if filters.sort_by:
            column = getattr(ProductModel, filters.sort_by, ProductModel.created_at)
            if filters.sort_order and filters.sort_order.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            # Default sorting by created_at
            query = query.order_by(ProductModel.created_at.desc())

        # Apply pagination
        query = query.offset(filters.offset).limit(filters.limit)

        # Execute queries
        result = await self._session.execute(query)
        count_result = await self._session.execute(count_query)

        product_models = result.scalars().all()
        total = count_result.scalar() or 0

        # Convert to domain entities
        products = [await self._to_domain_entity(model) for model in product_models]

        return products, total

    async def _to_domain_entity(self, model: ProductModel) -> Product:
        """Convert a ProductModel to a Product domain entity.

        Args:
            model: ProductModel instance

        Returns:
            Product domain entity
        """
        # Prepare categories
        categories = []
        if model.categories:
            for category in model.categories:
                categories.append(
                    {
                        "id": category.id,
                        "name": category.name,
                        "slug": category.slug,
                        "parentId": category.parent_id,
                    },
                )

        # Prepare images
        images = []
        if model.images:
            for image in model.images:
                images.append(
                    {
                        "id": str(image.id),
                        "url": image.url,
                        "alt": image.alt,
                        "isMain": image.is_main,
                        "order": image.order,
                    },
                )

        # Prepare variants
        variants = []
        if model.variants:
            for variant in model.variants:
                variant_data = {
                    "id": variant.id,
                    "sku": variant.sku,
                    "name": variant.name,
                    "price": float(variant.price_amount),
                    "compareAtPrice": (
                        float(variant.compare_at_price)
                        if variant.compare_at_price
                        else None
                    ),
                    "attributes": variant.attributes,
                    "stock": variant.stock,
                    "isAvailable": variant.is_available,
                    "isSelected": variant.is_selected,
                }
                variants.append(variant_data)

        # Prepare config options
        config_options = []
        if model.config_options:
            for option in model.config_options:
                config_options.append(
                    {
                        "id": str(option.id),
                        "name": option.name,
                        "values": option.values,
                    },
                )

        # Prepare reviews
        reviews = []
        if model.reviews:
            for review in model.reviews:
                review_data = {
                    "id": str(review.id),
                    "userId": review.user_id,
                    "userName": review.user_name,
                    "rating": review.rating,
                    "title": review.title,
                    "comment": review.comment,
                    "date": review.created_at.isoformat(),
                    "isVerifiedPurchase": review.is_verified_purchase,
                    "likes": review.likes,
                    "attributes": review.attributes,
                }
                reviews.append(review_data)

        # Create brand data if available
        brand = None
        if model.brand:
            brand = {
                "id": model.brand.id,
                "name": model.brand.name,
                "logo": model.brand.logo,
            }

        # Build product data dictionary
        product_data = {
            "id": model.id,
            "name": model.name,
            "slug": model.slug,
            "description": model.description,
            "summary": model.summary,
            "price": float(model.price_amount),
            "compareAtPrice": (
                float(model.compare_at_price) if model.compare_at_price else None
            ),
            "currency": model.price_currency,
            "brand": brand,
            "model": model.model,
            "sku": model.sku,
            "stock": model.stock,
            "isAvailable": model.is_available,
            "isNew": model.is_new,
            "isRefurbished": model.is_refurbished,
            "condition": model.condition,
            "categories": categories,
            "tags": model.tags,
            "images": images,
            "attributes": model.attributes,
            "hasVariants": model.has_variants,
            "variants": variants,
            "configOptions": config_options,
            "shipping": model.shipping,
            "warranty": model.warranty,
            "reviews": reviews,
            "highlightedFeatures": model.highlighted_features,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

        return Product(**product_data)
