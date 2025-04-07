"""Category API routes."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.dependencies import get_category_repository
from src.products.domain.model.category import Category
from src.products.domain.repositories.category_repository import CategoryRepository

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryCreateRequest(BaseModel):
    """Request model for creating a category."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryUpdateRequest(BaseModel):
    """Request model for updating a category."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryResponse(BaseModel):
    """Response model for category operations."""

    id: UUID
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    category: CategoryCreateRequest,
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryResponse:
    """Create a new category."""
    try:
        domain_category = Category(
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
        )
        result = await category_repository.create(domain_category)
        return _convert_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> List[CategoryResponse]:
    """List categories with pagination."""
    try:
        results = await category_repository.get_all(limit, offset)
        return [_convert_to_response(result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryResponse:
    """Get a category by ID."""
    try:
        result = await category_repository.get_by_id(category_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Category {category_id} not found",
            )
        return _convert_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category: CategoryUpdateRequest,
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryResponse:
    """Update a category."""
    try:
        # Get the existing category
        existing = await category_repository.get_by_id(category_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Category {category_id} not found",
            )

        # Create an updated domain model
        updated = Category(
            id=category_id,
            name=category.name if category.name is not None else existing.name,
            description=(
                category.description
                if category.description is not None
                else existing.description
            ),
            parent_id=(
                category.parent_id
                if category.parent_id is not None
                else existing.parent_id
            ),
        )

        result = await category_repository.update(updated)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Category {category_id} not found",
            )
        return _convert_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> None:
    """Delete a category."""
    try:
        result = await category_repository.delete(category_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Category {category_id} not found",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def _convert_to_response(category: Category) -> CategoryResponse:
    """Convert domain model to API response model."""
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        parent_id=category.parent_id,
    )
