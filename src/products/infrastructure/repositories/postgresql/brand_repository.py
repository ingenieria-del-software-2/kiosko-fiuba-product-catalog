"""Implementation of a BrandRepository using PostgreSQL."""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.products.application.dtos.product_dtos import (
    BrandCreateDTO,
    BrandUpdateDTO,
)
from src.products.domain.entities.product import Brand
from src.products.domain.repositories.brand_repository import BrandRepository
from src.products.infrastructure.repositories.postgresql.models import BrandModel


class PostgreSQLBrandRepository(BrandRepository):
    """PostgreSQL implementation of BrandRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create(self, brand_dto: BrandCreateDTO) -> Brand:
        """Create a new brand.

        Args:
            brand_dto: DTO with brand data

        Returns:
            Created brand entity
        """
        brand_model = BrandModel(
            name=brand_dto.name,
            logo=brand_dto.logo,
            description=brand_dto.description,
        )

        self._session.add(brand_model)
        await self._session.flush()

        return self._to_domain_entity(brand_model)

    async def get_by_id(self, brand_id: uuid.UUID) -> Optional[Brand]:
        """Get a brand by its ID.

        Args:
            brand_id: Brand ID

        Returns:
            Brand entity or None if not found
        """
        stmt = select(BrandModel).where(BrandModel.id == brand_id)
        result = await self._session.execute(stmt)
        brand_model = result.scalars().first()

        if not brand_model:
            return None

        return self._to_domain_entity(brand_model)

    async def get_by_name(self, name: str) -> Optional[Brand]:
        """Get a brand by its name.

        Args:
            name: Brand name

        Returns:
            Brand entity or None if not found
        """
        stmt = select(BrandModel).where(BrandModel.name == name)
        result = await self._session.execute(stmt)
        brand_model = result.scalars().first()

        if not brand_model:
            return None

        return self._to_domain_entity(brand_model)

    async def update(
        self,
        brand_id: uuid.UUID,
        brand_dto: BrandUpdateDTO,
    ) -> Optional[Brand]:
        """Update a brand.

        Args:
            brand_id: Brand ID
            brand_dto: DTO with updated brand data

        Returns:
            Updated brand entity or None if not found
        """
        stmt = select(BrandModel).where(BrandModel.id == brand_id)
        result = await self._session.execute(stmt)
        brand_model = result.scalars().first()

        if not brand_model:
            return None

        # Update fields if provided
        if brand_dto.name is not None:
            brand_model.name = brand_dto.name
        if brand_dto.logo is not None:
            brand_model.logo = brand_dto.logo
        if brand_dto.description is not None:
            brand_model.description = brand_dto.description

        # Update timestamp
        brand_model.updated_at = datetime.utcnow()

        await self._session.flush()

        return self._to_domain_entity(brand_model)

    async def delete(self, brand_id: uuid.UUID) -> bool:
        """Delete a brand.

        Args:
            brand_id: Brand ID

        Returns:
            True if deleted, False if not found
        """
        stmt = select(BrandModel).where(BrandModel.id == brand_id)
        result = await self._session.execute(stmt)
        brand_model = result.scalars().first()

        if not brand_model:
            return False

        await self._session.delete(brand_model)
        await self._session.flush()

        return True

    async def list(self, limit: int = 100, offset: int = 0) -> Tuple[List[Brand], int]:
        """List brands with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of brand entities and total count
        """
        # Query for data
        stmt = select(BrandModel).order_by(BrandModel.name).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        brand_models = result.scalars().all()

        # Query for count
        count_stmt = select(func.count()).select_from(BrandModel)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Convert to domain entities
        brands = [self._to_domain_entity(model) for model in brand_models]

        return brands, total

    def _to_domain_entity(self, model: BrandModel) -> Brand:
        """Convert a BrandModel to a Brand domain entity.

        Args:
            model: BrandModel instance

        Returns:
            Brand domain entity
        """
        return Brand(
            id=model.id,
            name=model.name,
            logo=model.logo,
        )
