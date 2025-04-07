"""Main API router module."""

from fastapi import APIRouter

from src.api.routes import categories, dummy, echo, monitoring, products

api_router = APIRouter()

# Include routes
api_router.include_router(monitoring.router, tags=["monitoring"])
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(products.router, tags=["products"])
api_router.include_router(categories.router, prefix="/products", tags=["products"])
