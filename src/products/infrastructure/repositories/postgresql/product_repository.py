"""PostgreSQL product repository implementation."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, column, func, insert, or_, select, table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductFilterDTO,
    ProductUpdateDTO,
)
from src.products.domain.entities.product import Product
from src.products.domain.repositories.product_repository import (
    ProductRepository,
)
from src.products.infrastructure.repositories.postgresql.models import (
    CategoryModel,
    ConfigOptionModel,
    ProductImageModel,
    ProductModel,
    ProductVariantModel,
    product_categories,
)


class PostgreSQLProductRepository(ProductRepository):
    """PostgreSQL implementation of the ProductRepository interface."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.

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
        import logging

        logger = logging.getLogger(__name__)

        # Create the product model
        product_model = ProductModel(
            name=product_dto.name,
            slug=product_dto.slug,
            description=product_dto.description,
            summary=product_dto.summary,
            price_amount=(
                product_dto.price_amount
                if hasattr(product_dto, "price_amount")
                else product_dto.price
            ),
            price_currency=product_dto.currency,
            compare_at_price=product_dto.compare_at_price,
            brand_id=product_dto.brand_id,
            model=product_dto.model,
            sku=product_dto.sku,
            stock=product_dto.stock,
            is_available=product_dto.is_available,
            is_new=product_dto.is_new,
            is_refurbished=product_dto.is_refurbished,
            condition=product_dto.condition,
            has_variants=product_dto.has_variants,
            tags=product_dto.tags,
            attributes=product_dto.attributes,
            highlighted_features=product_dto.highlighted_features,
            shipping=product_dto.shipping,
            warranty=product_dto.warranty,
        )

        self._session.add(product_model)

        try:
            # Flush to get product ID first - crucial for avoiding the greenlet error
            await self._session.flush()

            # Add categories if specified
            if product_dto.category_ids:
                await self._add_categories(product_model.id, product_dto.category_ids)

            # Add images if specified
            if product_dto.images:
                await self._add_images(product_model.id, product_dto.images)

            # Add variants if specified
            if product_dto.variants:
                await self._add_variants(
                    product_model.id,
                    product_dto.variants,
                    product_dto.currency,
                )

            # Add config options if specified
            if product_dto.config_options:
                await self._add_config_options(
                    product_model.id,
                    product_dto.config_options,
                )

            # Ensure all data is saved
            await self._session.flush()

            # Reload the product with all relationships to avoid lazy loading issues
            stmt = (
                select(ProductModel)
                .options(
                    selectinload(ProductModel.categories),
                    selectinload(ProductModel.images),
                    selectinload(ProductModel.variants).selectinload(
                        ProductVariantModel.images,
                    ),
                    joinedload(ProductModel.brand),
                )
                .where(ProductModel.id == product_model.id)
            )

            result = await self._session.execute(stmt)
            product_model = result.scalars().first()

            # Convert to domain entity
            return await self._to_domain_entity(product_model)

        except Exception as e:
            logger.error(f"Error creating product: {e!s}", exc_info=True)
            raise

    async def _add_categories(
        self,
        product_id: uuid.UUID,
        category_ids: List[uuid.UUID],
    ) -> None:
        """Add categories to a product using direct table operations to avoid ll."""
        # First, verify categories exist
        stmt = select(CategoryModel.id).where(CategoryModel.id.in_(category_ids))
        result = await self._session.execute(stmt)
        found_category_ids = [row[0] for row in result]

        # Insert directly into the association table
        product_categories_table = table(
            "product_categories",
            column("product_id"),
            column("category_id"),
        )

        for category_id in found_category_ids:
            insert_stmt = insert(product_categories_table).values(
                product_id=product_id,
                category_id=category_id,
            )
            await self._session.execute(insert_stmt)

        await self._session.flush()

    async def _add_images(self, product_id: uuid.UUID, images_data: List[Dict]) -> None:
        """Add images to a product."""
        for image_data in images_data:
            image = ProductImageModel(
                product_id=product_id,
                url=image_data["url"],
                alt=image_data.get("alt"),
                is_main=image_data.get("isMain", False),
                order=image_data.get("order", 0),
            )
            self._session.add(image)

    async def _add_variants(
        self,
        product_id: uuid.UUID,
        variants_data: List[Dict],
        currency: str,
    ) -> None:
        """Add variants to a product."""
        for variant_data in variants_data:
            variant = ProductVariantModel(
                parent_product_id=product_id,
                name=variant_data["name"],
                sku=variant_data["sku"],
                price_amount=variant_data["price"],
                price_currency=currency,
                compare_at_price=variant_data.get("compare_at_price"),
                stock=variant_data.get("stock", 0),
                is_available=variant_data.get("is_available", True),
                is_selected=variant_data.get("is_selected", False),
                attributes=variant_data.get("attributes", {}),
            )
            self._session.add(variant)

            # Flush to get variant ID
            await self._session.flush()

            # Add variant images if they exist
            if variant_data.get("images"):
                await self._add_variant_images(
                    product_id,
                    variant.id,
                    variant_data["images"],
                )

    async def _add_variant_images(
        self,
        product_id: uuid.UUID,
        variant_id: uuid.UUID,
        images_data: List[Dict],
    ) -> None:
        """Add images to a product variant."""
        for image_data in images_data:
            image = ProductImageModel(
                product_id=product_id,
                variant_id=variant_id,
                url=image_data["url"],
                alt=image_data.get("alt"),
                is_main=image_data.get("isMain", False),
                order=image_data.get("order", 0),
            )
            self._session.add(image)

    async def _add_config_options(
        self,
        product_id: uuid.UUID,
        config_options_data: List[Dict],
    ) -> None:
        """Add configuration options to a product."""
        for config_data in config_options_data:
            config = ConfigOptionModel(
                product_id=product_id,
                name=config_data["name"],
                values=config_data["values"],
            )
            self._session.add(config)

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
                selectinload(ProductModel.variants).selectinload(
                    ProductVariantModel.images,
                ),
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
                selectinload(ProductModel.variants).selectinload(
                    ProductVariantModel.images,
                ),
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
        product_model = await self._get_product_by_id(product_id)
        if not product_model:
            return None

        # Update different parts of the product
        self._update_basic_fields(product_model, product_dto)
        await self._update_categories(product_model, product_dto)
        await self._update_images(product_model, product_dto)
        await self._update_variants(product_model, product_dto)
        await self._update_config_options(product_model, product_dto)

        # Update timestamp
        product_model.updated_at = datetime.utcnow()
        await self._session.flush()

        # Convert to domain entity
        return await self._to_domain_entity(product_model)

    async def _get_product_by_id(self, product_id: uuid.UUID) -> Optional[ProductModel]:
        """Get product model by ID with related entities.

        Args:
            product_id: Product ID

        Returns:
            ProductModel or None if not found
        """
        stmt = (
            select(ProductModel)
            .options(
                selectinload(ProductModel.categories),
                selectinload(ProductModel.images),
                selectinload(ProductModel.variants).selectinload(
                    ProductVariantModel.images,
                ),
            )
            .where(ProductModel.id == product_id)
        )

        result = await self._session.execute(stmt)
        return result.scalars().first()

    def _update_basic_fields(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update basic fields of the product model.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        # Update different groups of fields
        self._update_name_and_description(product_model, product_dto)
        self._update_pricing(product_model, product_dto)
        self._update_inventory(product_model, product_dto)
        self._update_product_attributes(product_model, product_dto)
        self._update_product_features(product_model, product_dto)

    def _update_name_and_description(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update name, slug, description and summary fields.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        if product_dto.name is not None:
            product_model.name = product_dto.name
        if product_dto.slug is not None:
            product_model.slug = product_dto.slug
        if product_dto.description is not None:
            product_model.description = product_dto.description
        if product_dto.summary is not None:
            product_model.summary = product_dto.summary

    def _update_pricing(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update price related fields.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        if product_dto.price is not None:
            product_model.price_amount = product_dto.price
        if product_dto.compare_at_price is not None:
            product_model.compare_at_price = product_dto.compare_at_price
        if product_dto.currency is not None:
            product_model.price_currency = product_dto.currency

    def _update_inventory(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update inventory related fields.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        if product_dto.brand_id is not None:
            product_model.brand_id = product_dto.brand_id
        if product_dto.model is not None:
            product_model.model = product_dto.model
        if product_dto.sku is not None:
            product_model.sku = product_dto.sku
        if product_dto.stock is not None:
            product_model.stock = product_dto.stock

    def _update_product_attributes(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update product attributes and status fields.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        if product_dto.is_available is not None:
            product_model.is_available = product_dto.is_available
        if product_dto.is_new is not None:
            product_model.is_new = product_dto.is_new
        if product_dto.is_refurbished is not None:
            product_model.is_refurbished = product_dto.is_refurbished
        if product_dto.condition is not None:
            product_model.condition = product_dto.condition
        if product_dto.has_variants is not None:
            product_model.has_variants = product_dto.has_variants

    def _update_product_features(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update product features, tags, and additional data.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        if product_dto.tags is not None:
            product_model.tags = product_dto.tags
        if product_dto.attributes is not None:
            product_model.attributes = product_dto.attributes
        if product_dto.highlighted_features is not None:
            product_model.highlighted_features = product_dto.highlighted_features
        if product_dto.shipping is not None:
            product_model.shipping = product_dto.shipping
        if product_dto.warranty is not None:
            product_model.warranty = product_dto.warranty

    async def _update_categories(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update product categories.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        if product_dto.category_ids is not None:
            # Clear existing categories
            product_model.categories = []

            if product_dto.category_ids:
                stmt = select(CategoryModel).where(
                    CategoryModel.id.in_(product_dto.category_ids),
                )
                categories = (await self._session.execute(stmt)).scalars().all()
                product_model.categories = categories

    async def _update_images(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update product images.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        if product_dto.images is not None:
            # Delete existing images
            delete_stmt = select(ProductImageModel).where(
                ProductImageModel.product_id == product_model.id,
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
                    is_main=image_data.get("is_main", False),
                    order=image_data.get("order", 0),
                )
                self._session.add(image)

    async def _update_variants(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update product variants.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        if product_dto.variants is not None:
            # Delete existing variants
            delete_stmt = select(ProductVariantModel).where(
                ProductVariantModel.parent_product_id == product_model.id,
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
                    compare_at_price=variant_data.get("compare_at_price"),
                    stock=variant_data.get("stock", 0),
                    is_available=variant_data.get("is_available", True),
                    is_selected=variant_data.get("is_selected", False),
                    attributes=variant_data.get("attributes", {}),
                )
                self._session.add(variant)

    async def _update_config_options(
        self,
        product_model: ProductModel,
        product_dto: ProductUpdateDTO,
    ) -> None:
        """Update product configuration options.

        Args:
            product_model: Product model to update
            product_dto: DTO with updated product data
        """
        if product_dto.config_options is not None:
            # Delete existing config options
            delete_stmt = select(ConfigOptionModel).where(
                ConfigOptionModel.product_id == product_model.id,
            )
            existing_configs = (
                (await self._session.execute(delete_stmt)).scalars().all()
            )
            for config in existing_configs:
                await self._session.delete(config)

            # Add new config options
            for config_data in product_dto.config_options:
                config = ConfigOptionModel(
                    product_id=product_model.id,
                    name=config_data["name"],
                    values=config_data["values"],
                )
                self._session.add(config)

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

        # Build queries with filters
        query, count_query = self._build_list_queries(filters)

        # Execute queries
        result = await self._session.execute(query)
        count_result = await self._session.execute(count_query)

        product_models = result.scalars().all()
        total = count_result.scalar() or 0

        # Convert to domain entities
        products = [await self._to_domain_entity(model) for model in product_models]

        return products, total

    def _build_list_queries(
        self,
        filters: ProductFilterDTO,
    ) -> Tuple[Any, Any]:
        """Build list and count queries with filters applied.

        Args:
            filters: Filtering parameters

        Returns:
            Tuple of (list_query, count_query)
        """
        # Base query for data
        query = select(ProductModel).options(
            selectinload(ProductModel.categories),
            selectinload(ProductModel.images),
            joinedload(ProductModel.brand),
        )

        # Base query for count
        count_query = select(func.count()).select_from(ProductModel)

        # Apply filters
        conditions = self._build_filter_conditions(filters)

        # Add conditions to queries
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Apply sorting
        query = self._apply_sorting(query, filters)

        # Apply pagination
        query = query.offset(filters.offset).limit(filters.limit)

        return query, count_query

    def _build_filter_conditions(self, filters: ProductFilterDTO) -> List:
        """Build filter conditions for product queries.

        Args:
            filters: Filtering parameters

        Returns:
            List of filter conditions
        """
        conditions = []

        # Apply category, brand, and price filters
        conditions.extend(self._build_basic_filters(filters))

        # Apply search filters
        if filters.search:
            conditions.extend(self._build_search_filters(filters.search))

        # Apply additional filters
        conditions.extend(self._build_additional_filters(filters))

        return conditions

    def _build_basic_filters(self, filters: ProductFilterDTO) -> List:
        """Build basic filter conditions for category, brand, and price.

        Args:
            filters: Filtering parameters

        Returns:
            List of filter conditions
        """
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

        return conditions

    def _build_search_filters(self, search_term: str) -> List:
        """Build search filter conditions.

        Args:
            search_term: Search string

        Returns:
            List of filter conditions
        """
        formatted_term = f"%{search_term}%"
        return [
            or_(
                ProductModel.name.ilike(formatted_term),
                ProductModel.description.ilike(formatted_term),
                ProductModel.sku.ilike(formatted_term),
            ),
        ]

    def _build_additional_filters(self, filters: ProductFilterDTO) -> List:
        """Build additional filter conditions for tags and status.

        Args:
            filters: Filtering parameters

        Returns:
            List of filter conditions
        """
        conditions = []

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

        return conditions

    def _apply_sorting(
        self,
        query: Any,
        filters: ProductFilterDTO,
    ) -> Any:
        """Apply sorting to the query.

        Args:
            query: The query to apply sorting to
            filters: Filtering parameters with sorting info

        Returns:
            Query with sorting applied
        """
        if filters.sort_by:
            column = getattr(ProductModel, filters.sort_by, ProductModel.created_at)
            if filters.sort_order and filters.sort_order.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            # Default sorting by created_at
            query = query.order_by(ProductModel.created_at.desc())

        return query

    async def _to_domain_entity(self, model: ProductModel) -> Product:
        """Convert a ProductModel to a Product domain entity.

        Args:
            model: SQL Alchemy model

        Returns:
            Domain entity
        """
        # Prepare all data for the domain entity
        product_data = {
            "id": model.id,
            "name": model.name,
            "slug": model.slug,
            "description": model.description,
            "summary": model.summary,
            "price": float(model.price_amount),
            "compare_at_price": (
                float(model.compare_at_price) if model.compare_at_price else None
            ),
            "currency": model.price_currency,
            "sku": model.sku,
            "stock": model.stock,
            "is_available": model.is_available,
            "is_new": model.is_new,
            "is_refurbished": model.is_refurbished,
            "condition": model.condition,
            "model": model.model,
            "has_variants": model.has_variants,
            "tags": model.tags or [],
            "attributes": model.attributes or [],
            "highlighted_features": model.highlighted_features or [],
            "shipping": model.shipping,
            "warranty": model.warranty,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        }

        # Process relationships
        if hasattr(model, "categories") and model.categories:
            product_data["categories"] = self._prepare_categories(model.categories)

        if hasattr(model, "images") and model.images:
            # Get only product-level images (not variant images)
            product_images = [img for img in model.images if img.variant_id is None]
            if product_images:
                product_data["images"] = self._prepare_images(product_images)

        if hasattr(model, "variants") and model.variants:
            product_data["variants"] = self._prepare_variants(model.variants)

        if hasattr(model, "config_options") and model.config_options:
            product_data["config_options"] = self._prepare_config_options(
                model.config_options,
            )

        if hasattr(model, "brand") and model.brand:
            product_data["brand"] = self._prepare_brand(model.brand)

        if hasattr(model, "reviews") and model.reviews:
            product_data["reviews"] = self._prepare_reviews(model.reviews)

        try:
            # Create domain entity from prepared data
            return Product(**product_data)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(
                f"Error creating Product domain entity: {e!s}",
                exc_info=True,
            )
            raise

    def _prepare_categories(
        self,
        categories: List[CategoryModel],
    ) -> List[dict]:
        """Prepare categories for domain entity.

        Args:
            categories: List of category models

        Returns:
            List of category dictionaries
        """
        result = []
        if categories:
            for category in categories:
                result.append(
                    {
                        "id": category.id,
                        "name": category.name,
                        "slug": category.slug,
                        "parentId": category.parent_id,
                    },
                )
        return result

    def _prepare_images(
        self,
        images: List[ProductImageModel],
    ) -> List[dict]:
        """Prepare images for domain entity.

        Args:
            images: List of image models

        Returns:
            List of image dictionaries
        """
        result = []
        if images:
            for image in images:
                result.append(
                    {
                        "id": str(image.id),
                        "url": image.url,
                        "alt": image.alt,
                        "is_main": image.is_main,
                        "order": image.order,
                    },
                )
        return result

    def _prepare_variants(
        self,
        variants: List[ProductVariantModel],
    ) -> List[dict]:
        """Prepare variants for domain entity.

        Args:
            variants: List of variant models

        Returns:
            List of variant dictionaries
        """
        result = []
        if variants:
            for variant in variants:
                variant_data = {
                    "id": variant.id,
                    "sku": variant.sku,
                    "name": variant.name,
                    "price": float(variant.price_amount),
                    "compare_at_price": (
                        float(variant.compare_at_price)
                        if variant.compare_at_price
                        else None
                    ),
                    "attributes": variant.attributes,
                    "stock": variant.stock,
                    "is_available": variant.is_available,
                    "is_selected": variant.is_selected,
                }
                result.append(variant_data)
        return result

    def _prepare_config_options(
        self,
        config_options: List[ConfigOptionModel],
    ) -> List[dict]:
        """Prepare config options for domain entity.

        Args:
            config_options: List of config option models

        Returns:
            List of config option dictionaries
        """
        result = []
        if config_options:
            for option in config_options:
                result.append(
                    {
                        "id": str(option.id),
                        "name": option.name,
                        "values": option.values,
                    },
                )
        return result

    def _prepare_reviews(
        self,
        reviews: List[Any],
    ) -> List[dict]:
        """Prepare reviews for domain entity.

        Args:
            reviews: List of review models

        Returns:
            List of review dictionaries
        """
        result = []
        if reviews:
            for review in reviews:
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
                result.append(review_data)
        return result

    def _prepare_brand(
        self,
        brand: Any,
    ) -> Optional[dict]:
        """Prepare brand for domain entity.

        Args:
            brand: Brand model

        Returns:
            Brand dictionary or None
        """
        if not brand:
            return None

        return {
            "id": brand.id,
            "name": brand.name,
            "logo": brand.logo,
        }
