"""API router configuration."""

from fastapi import APIRouter

from src.api.routes import brands, categories, dummy, echo, health, products

# Create main router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, prefix="/health")
api_router.include_router(products.router, prefix="/products")
api_router.include_router(categories.router, prefix="/categories")
api_router.include_router(brands.router, prefix="/brands")
api_router.include_router(dummy.router, prefix="/dummy")
api_router.include_router(echo.router, prefix="/echo")
