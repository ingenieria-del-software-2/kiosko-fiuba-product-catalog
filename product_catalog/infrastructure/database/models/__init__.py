from .dummy_model import DummyModel

__all__ = ["DummyModel"]


def load_all_models() -> None:
    """Load all models to register them with the Base metadata."""
    # Add any additional model imports here if needed
