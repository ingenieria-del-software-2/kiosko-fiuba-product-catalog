"""PostgreSQL implementation of the Dummy repository."""

from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dummy.domain.model.dummy import Dummy
from src.dummy.domain.repositories.interfaces.dummy_repository import (
    DummyRepository,
)
from src.dummy.infrastructure.repositories.postgresql.model.dummy_model import (
    DummyModel,
)
from src.shared.database.dependencies import get_db_session


class PostgreSQLDummyRepository(DummyRepository):
    """PostgreSQL implementation of the Dummy repository."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        """
        Initialize the repository with a database session.

        Args:
            session: Database session
        """
        self.session = session

    async def get_all(self, limit: int, offset: int) -> List[Dummy]:
        """
        Get all dummy entities with pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of Dummy entities
        """
        raw_dummies = await self.session.execute(
            select(DummyModel).limit(limit).offset(offset),
        )

        dummy_models = list(raw_dummies.scalars().fetchall())
        return [self._map_to_domain(model) for model in dummy_models]

    async def get_by_id(self, dummy_id: int) -> Optional[Dummy]:
        """
        Get a dummy entity by its ID.

        Args:
            dummy_id: ID of the dummy entity

        Returns:
            Dummy entity if found, None otherwise
        """
        result = await self.session.execute(
            select(DummyModel).where(DummyModel.id == dummy_id),
        )
        dummy_model = result.scalars().first()

        if not dummy_model:
            return None

        return self._map_to_domain(dummy_model)

    async def create(self, dummy: Dummy) -> Dummy:
        """
        Create a new dummy entity.

        Args:
            dummy: Dummy entity to create

        Returns:
            Created dummy entity with ID
        """
        dummy_model = DummyModel(name=dummy.name)
        self.session.add(dummy_model)
        await self.session.flush()

        return self._map_to_domain(dummy_model)

    async def find_by_name(self, name: str) -> List[Dummy]:
        """
        Find dummy entities by name.

        Args:
            name: Name to search for

        Returns:
            List of matching Dummy entities
        """
        result = await self.session.execute(
            select(DummyModel).where(DummyModel.name == name),
        )

        dummy_models = list(result.scalars().fetchall())
        return [self._map_to_domain(model) for model in dummy_models]

    def _map_to_domain(self, model: DummyModel) -> Dummy:
        """
        Map a database model to a domain entity.

        Args:
            model: Database model

        Returns:
            Domain entity
        """
        return Dummy(id=model.id, name=model.name)
