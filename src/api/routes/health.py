"""Health check routes."""

from fastapi import APIRouter, status
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    version: str


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API is running correctly",
)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        Health status response
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
    )
