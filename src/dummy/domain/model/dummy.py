"""Dummy domain entity module."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Dummy:
    """Dummy domain entity."""

    name: str
    id: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate the entity after initialization."""
        if not self.name:
            raise ValueError("Dummy name cannot be empty")
