"""Routes for brand endpoints."""

import uuid
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.products.application.dtos.product_dtos import (
    BrandCreateDTO,
    BrandUpdateDTO,
)
from src.products.application.services.brand_service import BrandService
from src.products.domain.entities.product import Brand
from src.products.infrastructure.repositories.postgresql.brand_repository import (
    PostgreSQLBrandRepository,
)
from src.shared.database.dependencies import get_db_session

router = APIRouter(
    prefix="/brands",
    tags=["Brands"],
)


async def get_brand_service(
    db_session: AsyncSession = Depends(get_db_session),
) -> BrandService:
    """Dependency for getting the brand service.

    Args:
        db_session: Database session

    Returns:
        Initialized brand service
    """
    repository = PostgreSQLBrandRepository(db_session)
    return BrandService(repository)


@router.post(
    "",
    response_model=Brand,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new brand",
    description="Create a new brand with the provided data",
)
async def create_brand(
    brand_data: BrandCreateDTO,
    brand_service: BrandService = Depends(get_brand_service),
) -> Brand:
    """Create a new brand.

    Args:
        brand_data: Data for the new brand
        brand_service: Brand service dependency

    Returns:
        Created brand data
    """
    return await brand_service.create_brand(brand_data)


@router.get(
    "/{brand_id}",
    response_model=Brand,
    summary="Get a brand by ID",
    description="Get detailed information about a brand by its ID",
)
async def get_brand(
    brand_id: uuid.UUID = Path(..., description="The ID of the brand to get"),
    brand_service: BrandService = Depends(get_brand_service),
) -> Brand:
    """Get a brand by ID.

    Args:
        brand_id: ID of the brand to get
        brand_service: Brand service dependency

    Returns:
        Brand data

    Raises:
        HTTPException: If brand not found
    """
    brand = await brand_service.get_brand_by_id(brand_id)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with ID {brand_id} not found",
        )

    return brand


@router.get(
    "/name/{name}",
    response_model=Brand,
    summary="Get a brand by name",
    description="Get detailed information about a brand by its name",
)
async def get_brand_by_name(
    name: str = Path(..., description="The name of the brand to get"),
    brand_service: BrandService = Depends(get_brand_service),
) -> Brand:
    """Get a brand by name.

    Args:
        name: Name of the brand to get
        brand_service: Brand service dependency

    Returns:
        Brand data

    Raises:
        HTTPException: If brand not found
    """
    brand = await brand_service.get_brand_by_name(name)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with name {name} not found",
        )

    return brand


@router.put(
    "/{brand_id}",
    response_model=Brand,
    summary="Update a brand",
    description="Update a brand with the provided data",
)
async def update_brand(
    brand_data: BrandUpdateDTO,
    brand_id: uuid.UUID = Path(..., description="The ID of the brand to update"),
    brand_service: BrandService = Depends(get_brand_service),
) -> Brand:
    """Update a brand.

    Args:
        brand_data: Data for updating the brand
        brand_id: ID of the brand to update
        brand_service: Brand service dependency

    Returns:
        Updated brand data

    Raises:
        HTTPException: If brand not found
    """
    brand = await brand_service.update_brand(brand_id, brand_data)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with ID {brand_id} not found",
        )

    return brand


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a brand",
    description="Delete a brand by its ID",
)
async def delete_brand(
    brand_id: uuid.UUID = Path(..., description="The ID of the brand to delete"),
    brand_service: BrandService = Depends(get_brand_service),
) -> None:
    """Delete a brand.

    Args:
        brand_id: ID of the brand to delete
        brand_service: Brand service dependency

    Raises:
        HTTPException: If brand not found
    """
    deleted = await brand_service.delete_brand(brand_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with ID {brand_id} not found",
        )


@router.get(
    "",
    response_model=Dict[str, object],
    summary="List brands",
    description="List brands with pagination",
)
async def list_brands(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    brand_service: BrandService = Depends(get_brand_service),
) -> Dict[str, object]:
    """List brands with pagination.

    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        brand_service: Brand service dependency

    Returns:
        Dictionary with brands and metadata
    """
    brands, total = await brand_service.list_brands(limit, offset)

    return {
        "items": brands,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
