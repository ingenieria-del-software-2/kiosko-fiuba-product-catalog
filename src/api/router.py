"""API router configuration."""

from fastapi import APIRouter

from src.api.routes import brands, categories, health, products

# Create main router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router)
api_router.include_router(products.router)
api_router.include_router(categories.router)
api_router.include_router(brands.router)
