"""PostgreSQL implementation of the CategoryRepository interface."""

import uuid
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.products.domain.model.category import Category
from src.products.domain.repositories.category_repository import CategoryRepository
from src.products.infrastructure.repositories.postgresql.models import CategoryModel


class PostgresCategoryRepository(CategoryRepository):
    """PostgreSQL implementation of the CategoryRepository interface."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            session: Database session.
        """
        self.session = session

    async def create(self, category: Category) -> Category:
        """
        Create a new category.

        Args:
            category: The category to create.

        Returns:
            The created category.
        """
        model = CategoryModel(
            id=category.id or uuid.uuid4(),
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
        )
        self.session.add(model)
        await self.session.flush()

        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
        )

    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """
        Get a category by ID.

        Args:
            category_id: The ID of the category to get.

        Returns:
            The category, or None if not found.
        """
        query = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.session.execute(query)
        model = result.scalars().first()

        if model is None:
            return None

        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
        )

    async def get_by_name(self, name: str) -> Optional[Category]:
        """
        Get a category by name.

        Args:
            name: The name of the category to get.

        Returns:
            The category, or None if not found.
        """
        query = select(CategoryModel).where(CategoryModel.name == name)
        result = await self.session.execute(query)
        model = result.scalars().first()

        if model is None:
            return None

        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
        )

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Category]:
        """
        Get all categories.

        Args:
            limit: Maximum number of categories to return.
            offset: Number of categories to skip.

        Returns:
            List of categories.
        """
        query = select(CategoryModel).limit(limit).offset(offset)
        result = await self.session.execute(query)
        models = result.scalars().all()

        return [
            Category(
                id=model.id,
                name=model.name,
                description=model.description,
                parent_id=model.parent_id,
            )
            for model in models
        ]

    async def list_categories(
        self,
        parent_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Category]:
        """
        List categories with optional parent filter and pagination.

        Args:
            parent_id: Optional parent category ID to filter by.
            limit: Maximum number of categories to return.
            offset: Number of categories to skip.

        Returns:
            List of categories.
        """
        if parent_id is None:
            query = select(CategoryModel).limit(limit).offset(offset)
        else:
            query = (
                select(CategoryModel)
                .where(CategoryModel.parent_id == parent_id)
                .limit(limit)
                .offset(offset)
            )

        result = await self.session.execute(query)
        models = result.scalars().all()

        return [
            Category(
                id=model.id,
                name=model.name,
                description=model.description,
                parent_id=model.parent_id,
            )
            for model in models
        ]

    async def update(self, category: Category) -> Category:
        """
        Update a category.

        Args:
            category: The category to update.

        Returns:
            The updated category, or None if not found.
        """
        query = select(CategoryModel).where(CategoryModel.id == category.id)
        result = await self.session.execute(query)
        model = result.scalars().first()

        if model is None:
            raise ValueError(f"Category with ID {category.id} not found")

        model.name = category.name
        model.description = category.description
        model.parent_id = category.parent_id

        await self.session.flush()

        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
        )

    async def delete(self, category_id: UUID) -> bool:
        """
        Delete a category.

        Args:
            category_id: The ID of the category to delete.

        Returns:
            True if the category was deleted, False if not found.
        """
        query = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.session.execute(query)
        model = result.scalars().first()

        if model is None:
            return False

        await self.session.delete(model)
        await self.session.flush()

        return True
