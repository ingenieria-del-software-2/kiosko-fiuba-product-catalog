"""Routes for product endpoints."""

import uuid
from typing import Any, Dict, List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.products.application.dtos.product_dtos import (
    ProductCreateDTO,
    ProductFilterDTO,
    ProductResponseDTO,
    ProductUpdateDTO,
)
from src.products.application.services.product_service import ProductService
from src.products.domain.exceptions.domain_exceptions import ProductNotFoundError
from src.products.infrastructure.repositories.postgresql.category_repository import (
    PostgresCategoryRepository,
)
from src.products.infrastructure.repositories.postgresql.product_repository import (
    PostgreSQLProductRepository,
)
from src.shared.database.dependencies import get_db_session
from src.shared.event_publisher.console_publisher import ConsoleEventPublisher

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


async def get_product_service(
    db_session: AsyncSession = Depends(get_db_session),
) -> ProductService:
    """Dependency for getting the product service.

    Args:
        db_session: Database session

    Returns:
        Initialized product service
    """
    product_repository = PostgreSQLProductRepository(db_session)
    category_repository = PostgresCategoryRepository(db_session)
    event_publisher = ConsoleEventPublisher()
    return ProductService(
        product_repository=product_repository,
        category_repository=category_repository,
        event_publisher=event_publisher,
    )


@router.post(
    "",
    response_model=ProductResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Create a new product with the provided data",
)
async def create_product(
    product_data: ProductCreateDTO,
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponseDTO:
    """Create a new product.

    Args:
        product_data: Data for the new product
        product_service: Product service dependency

    Returns:
        Created product data
    """
    return await product_service.create_product(product_data)


@router.get(
    "/{product_id}",
    response_model=ProductResponseDTO,
    summary="Get a product by ID",
    description="Get detailed information about a product by its ID",
)
async def get_product(
    product_id: uuid.UUID = Path(..., description="The ID of the product to get"),
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponseDTO:
    """Get a product by ID.

    Args:
        product_id: ID of the product to get
        product_service: Product service dependency

    Returns:
        Product data

    Raises:
        HTTPException: If product not found
    """
    try:
        product = await product_service.get_product_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return cast(ProductResponseDTO, product)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get(
    "/sku/{sku}",
    response_model=ProductResponseDTO,
    summary="Get a product by SKU",
    description="Get detailed information about a product by its SKU",
)
async def get_product_by_sku(
    sku: str = Path(..., description="The SKU of the product to get"),
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponseDTO:
    """Get a product by SKU.

    Args:
        sku: SKU of the product to get
        product_service: Product service dependency

    Returns:
        Product data

    Raises:
        HTTPException: If product not found
    """
    product = await product_service.get_product_by_sku(sku)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with SKU {sku} not found",
        )

    return cast(ProductResponseDTO, product)


@router.put(
    "/{product_id}",
    response_model=ProductResponseDTO,
    summary="Update a product",
    description="Update a product with the provided data",
)
async def update_product(
    product_data: ProductUpdateDTO,
    product_id: uuid.UUID = Path(..., description="The ID of the product to update"),
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponseDTO:
    """Update a product.

    Args:
        product_data: Data for updating the product
        product_id: ID of the product to update
        product_service: Product service dependency

    Returns:
        Updated product data

    Raises:
        HTTPException: If product not found
    """
    # Convert camelCase to snake_case for fields that need adjustment
    if hasattr(product_data, "compareAtPrice"):
        product_data.compare_at_price = product_data.compareAtPrice  # type: ignore
    if hasattr(product_data, "isAvailable"):
        product_data.is_available = product_data.isAvailable  # type: ignore
    if hasattr(product_data, "isNew"):
        product_data.is_new = product_data.isNew  # type: ignore
    if hasattr(product_data, "isRefurbished"):
        product_data.is_refurbished = product_data.isRefurbished  # type: ignore
    if hasattr(product_data, "hasVariants"):
        product_data.has_variants = product_data.hasVariants  # type: ignore
    if hasattr(product_data, "highlightedFeatures"):
        product_data.highlighted_features = product_data.highlightedFeatures  # type: ignore
    if hasattr(product_data, "configOptions"):
        product_data.config_options = product_data.configOptions  # type: ignore

    try:
        result = await product_service.update_product(product_id, product_data)
        return cast(ProductResponseDTO, result)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    description="Delete a product by its ID",
)
async def delete_product(
    product_id: uuid.UUID = Path(..., description="The ID of the product to delete"),
    product_service: ProductService = Depends(get_product_service),
) -> None:
    """Delete a product.

    Args:
        product_id: ID of the product to delete
        product_service: Product service dependency

    Raises:
        HTTPException: If product not found
    """
    try:
        await product_service.delete_product(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get(
    "",
    response_model=Dict[str, Any],
    summary="List products",
    description="List products with optional filtering and pagination",
)
async def list_products(
    category_id: Optional[uuid.UUID] = Query(None, description="Filter by category ID"),
    brand_id: Optional[uuid.UUID] = Query(None, description="Filter by brand ID"),
    price_min: Optional[float] = Query(None, description="Minimum price filter"),
    price_max: Optional[float] = Query(None, description="Maximum price filter"),
    search: Optional[str] = Query(None, description="Search query"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    is_new: Optional[bool] = Query(None, description="Filter by new status"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    product_service: ProductService = Depends(get_product_service),
) -> Dict[str, Any]:
    """List products with filtering and pagination.

    Args:
        Various filter parameters
        product_service: Product service dependency

    Returns:
        Dictionary with products and metadata
    """
    filters = ProductFilterDTO(
        category_id=category_id,
        brand_id=brand_id,
        price_min=price_min,
        price_max=price_max,
        search=search,
        tags=tags,
        is_available=is_available,
        is_new=is_new,
        condition=condition,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )

    products, total = await product_service.list_products(filters)

    return {
        "items": products,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
