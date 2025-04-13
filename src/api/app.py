"""FastAPI application setup."""

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
import os

from src.api.lifespan import lifespan
from src.api.router import api_router


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    api_path_prefix = os.getenv("API_PATH_PREFIX", "")
    
    app = FastAPI(
        title="product_catalog",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
        root_path=api_path_prefix,
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app