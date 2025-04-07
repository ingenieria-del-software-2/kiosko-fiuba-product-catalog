"""Main API router module."""

from fastapi import APIRouter

from product_catalog.api.routes import dummy, echo, monitoring

api_router = APIRouter()

# Include routes
api_router.include_router(monitoring.router, tags=["monitoring"])
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
