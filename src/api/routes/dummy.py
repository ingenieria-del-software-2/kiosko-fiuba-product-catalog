"""API routes for the dummy domain."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_dummy_service
from src.dummy.application.dtos.dummy_dtos import CreateDummyDTO, DummyDTO
from src.dummy.application.services.dummy_service import DummyService
from src.dummy.domain.exceptions.domain_exceptions import DummyNotFoundError

router = APIRouter()


@router.get("/", response_model=List[DummyDTO])
async def get_dummies(
    limit: int = 10,
    offset: int = 0,
    dummy_service: DummyService = Depends(get_dummy_service),
) -> List[DummyDTO]:
    """
    Get all dummy entities with pagination.

    Args:
        limit: Maximum number of entities to return
        offset: Number of entities to skip
        dummy_service: Service for managing dummy entities

    Returns:
        List of DummyDTO objects
    """
    return await dummy_service.get_all_dummies(limit=limit, offset=offset)


@router.post("/", response_model=DummyDTO, status_code=status.HTTP_201_CREATED)
async def create_dummy(
    dto: CreateDummyDTO,
    dummy_service: DummyService = Depends(get_dummy_service),
) -> DummyDTO:
    """
    Create a new dummy entity.

    Args:
        dto: DTO with data for the new entity
        dummy_service: Service for managing dummy entities

    Returns:
        DTO of the created entity
    """
    return await dummy_service.create_dummy(dto)


@router.get("/search/", response_model=List[DummyDTO])
async def search_dummies_by_name(
    name: str,
    dummy_service: DummyService = Depends(get_dummy_service),
) -> List[DummyDTO]:
    """
    Find dummy entities by name.

    Args:
        name: Name to search for
        dummy_service: Service for managing dummy entities

    Returns:
        List of matching DummyDTO objects
    """
    return await dummy_service.find_dummies_by_name(name)


@router.get("/{dummy_id}", response_model=DummyDTO)
async def get_dummy_by_id(
    dummy_id: int,
    dummy_service: DummyService = Depends(get_dummy_service),
) -> DummyDTO:
    """
    Get a dummy entity by its ID.

    Args:
        dummy_id: ID of the entity to get
        dummy_service: Service for managing dummy entities

    Returns:
        DTO of the entity

    Raises:
        HTTPException: If the entity is not found
    """
    try:
        return await dummy_service.get_dummy_by_id(dummy_id)
    except DummyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
