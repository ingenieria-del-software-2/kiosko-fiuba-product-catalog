"""API routes for monitoring."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", name="health_check")
def health_check() -> dict[str, str]:
    """
    Checks the health of the application.

    Returns:
        Status message indicating the application is healthy
    """
    return {"status": "ok"}
