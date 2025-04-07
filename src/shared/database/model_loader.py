"""Module for dynamically loading all SQLAlchemy models."""

import importlib
import pkgutil
from contextlib import suppress
from pathlib import Path
from typing import List


def _find_model_modules() -> List[str]:
    """
    Find all potential model modules in the project.

    Searches for files matching *_model.py in the src directory.

    Returns:
        List of module names that might contain SQLAlchemy models
    """
    model_modules = []
    src_dir = Path(__file__).parent.parent.parent  # Navigate to src directory

    # Look for model packages and modules
    for module_info in pkgutil.walk_packages(
        path=[str(src_dir)],
        prefix="src.",
    ):
        if (
            "model" in module_info.name.lower()
            or module_info.name.lower().endswith("_model")
            or module_info.name.lower().endswith("_models")
        ):
            model_modules.append(module_info.name)

    # Also check for domain-specific models in repositories
    for model_dir in src_dir.glob("**/repositories/**/model*"):
        if model_dir.is_dir():
            package_path = model_dir.relative_to(src_dir.parent)
            package_name = str(package_path).replace("/", ".")
            model_modules.append(package_name)

    # Add specific model paths that might be missed
    model_files = [
        p
        for p in src_dir.glob("**/models.py")
        if "infrastructure" in str(p) and "repositories" in str(p)
    ]

    for model_file in model_files:
        package_path = model_file.relative_to(src_dir.parent).with_suffix("")
        package_name = str(package_path).replace("/", ".")
        if package_name not in model_modules:
            model_modules.append(package_name)

    return model_modules


def load_all_models() -> None:
    """
    Load all SQLAlchemy models to ensure they're registered with metadata.

    This function dynamically discovers and imports all potential model modules
    across the codebase to ensure their SQLAlchemy models are registered with
    the metadata for migrations.
    """
    # Find and import all potential model modules
    model_modules = _find_model_modules()

    # Explicitly import known model modules to ensure they're loaded
    with suppress(ImportError):
        import src.products.infrastructure.repositories.postgresql.models  # noqa
        import src.dummy.infrastructure.repositories.postgresql.models  # noqa

    # Import dynamically discovered modules
    for module_name in model_modules:
        with suppress(ImportError):
            importlib.import_module(module_name)
