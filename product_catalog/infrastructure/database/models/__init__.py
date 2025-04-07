"""Database models package."""

from product_catalog.infrastructure.database.models.dummy_model import (
    DummyModel,  # noqa: F401
)


def load_all_models() -> None:
    """
    Load all models to register them with SQLAlchemy.
    
    This function doesn't do anything explicit as importing the models
    is sufficient for the SQLAlchemy registration process.
    """
