"""FastAPI application setup."""

from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from src.api.lifespan import lifespan
from src.api.router import api_router


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="product_catalog",
        version=metadata.version("product_catalog"),
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
