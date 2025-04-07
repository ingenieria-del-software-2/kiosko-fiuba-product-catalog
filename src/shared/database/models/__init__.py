from src.shared.database.models.dummy_model import DummyModel

__all__ = ["DummyModel"]


def load_all_models() -> None:
    """Load all models to register them with the Base metadata."""
    # This function is called to ensure all models are imported
    # and registered with SQLAlchemy's Base metadata
    pass  # The imports above are sufficient
