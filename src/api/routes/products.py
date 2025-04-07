"""Product API routes."""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.dependencies import get_product_service
from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductResponseDTO,
    ProductUpdateDTO,
)
from src.products.application.services.product_service import ProductService
from src.products.domain.exceptions.domain_exceptions import (
    CategoryNotFoundError,
    ProductNotFoundError,
)

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreateRequest(BaseModel):
    """Request model for creating a product."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    category_id: UUID
    sku: str = Field(..., min_length=1, max_length=100)
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ProductUpdateRequest(BaseModel):
    """Request model for updating a product."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    category_id: Optional[UUID] = None
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None


class ProductResponse(BaseModel):
    """Response model for product operations."""

    id: UUID
    name: str
    description: str
    price: float
    currency: str
    category_id: UUID
    sku: str
    status: str
    images: List[str]
    tags: List[str]
    attributes: Dict[str, Any]
    created_at: str
    updated_at: str


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreateRequest,
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Create a new product."""
    try:
        product_dto = ProductCreateDTO(
            name=product.name,
            description=product.description,
            price=Decimal(str(product.price)),
            currency=product.currency,
            category_id=product.category_id,
            sku=product.sku,
            images=product.images,
            tags=product.tags,
            attributes=product.attributes,
        )
        result = await product_service.create_product(product_dto)
        return _convert_to_response(result)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("", response_model=List[ProductResponse])
async def list_products(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    product_service: ProductService = Depends(get_product_service),
) -> List[ProductResponse]:
    """List products with pagination."""
    try:
        results = await product_service.list_products(limit, offset)
        return [_convert_to_response(result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    query: str = Query(..., min_length=1),
    category_id: Optional[UUID] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    product_service: ProductService = Depends(get_product_service),
) -> List[ProductResponse]:
    """Search products by name, description or category."""
    try:
        results = await product_service.search_products(
            query,
            category_id,
            limit,
            offset,
        )
        return [_convert_to_response(result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/category/{category_id}", response_model=List[ProductResponse])
async def get_products_by_category(
    category_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    product_service: ProductService = Depends(get_product_service),
) -> List[ProductResponse]:
    """Get products by category."""
    try:
        results = await product_service.get_products_by_category(
            category_id,
            limit,
            offset,
        )
        return [_convert_to_response(result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Get a product by ID."""
    try:
        result = await product_service.get_product(product_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found",
            )
        return _convert_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product: ProductUpdateRequest,
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Update a product."""
    try:
        # Convert float price to Decimal if it's not None
        price = Decimal(str(product.price)) if product.price is not None else None

        product_dto = ProductUpdateDTO(
            id=product_id,
            name=product.name,
            description=product.description,
            price=price,
            currency=product.currency,
            category_id=product.category_id,
            sku=product.sku,
            status=product.status,
            images=product.images,
            tags=product.tags,
            attributes=product.attributes,
        )
        result = await product_service.update_product(product_dto)
        return _convert_to_response(result)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Product {product_id} not found",
        ) from e
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    product_service: ProductService = Depends(get_product_service),
) -> None:
    """Delete a product."""
    try:
        result = await product_service.delete_product(product_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found",
            )
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Product {product_id} not found",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def _convert_to_response(dto: ProductResponseDTO) -> ProductResponse:
    """Convert DTO to API response model."""
    return ProductResponse(
        id=dto.id,
        name=dto.name,
        description=dto.description,
        price=float(dto.price),
        currency=dto.currency,
        category_id=dto.category_id,
        sku=dto.sku,
        status=dto.status,
        images=dto.images,
        tags=dto.tags,
        attributes=dto.attributes,
        created_at=dto.created_at.isoformat(),
        updated_at=dto.updated_at.isoformat(),
    )
