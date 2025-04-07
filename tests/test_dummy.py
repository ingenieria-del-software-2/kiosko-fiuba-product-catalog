import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from product_catalog.domain.model.dummy import Dummy
from product_catalog.infrastructure.repositories.postgresql.dummy_repository import (
    PostgreSQLDummyRepository,
)


@pytest.mark.anyio
async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests dummy instance creation."""
    test_name = uuid.uuid4().hex

    # Using the new API route
    response = await client.post("/api/dummy/", json={"name": test_name})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == test_name

    # Verify it was created in the database
    repo = PostgreSQLDummyRepository(session=dbsession)
    dummies = await repo.find_by_name(test_name)

    assert len(dummies) == 1
    assert dummies[0].name == test_name


@pytest.mark.anyio
async def test_getting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests dummy instance retrieval."""
    test_name = uuid.uuid4().hex

    # Create a test dummy using the repository
    repo = PostgreSQLDummyRepository(session=dbsession)
    dummy = await repo.create(Dummy(name=test_name))

    # Test getting all dummies
    response = await client.get("/api/dummy/")
    dummies = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(dummies) >= 1

    # Find our test dummy in the results
    matching = [d for d in dummies if d["name"] == test_name]
    assert len(matching) == 1

    # Test getting by ID
    response = await client.get(f"/api/dummy/{dummy.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == test_name

    # Test search by name
    response = await client.get(f"/api/dummy/search/?name={test_name}")
    assert response.status_code == status.HTTP_200_OK
    search_results = response.json()
    assert len(search_results) == 1
    assert search_results[0]["name"] == test_name
