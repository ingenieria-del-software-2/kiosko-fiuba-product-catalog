"""Category Data Transfer Objects."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class CategoryCreateDTO:
    """DTO for creating a new category."""

    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


@dataclass
class CategoryUpdateDTO:
    """DTO for updating an existing category."""

    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


@dataclass
class CategoryResponseDTO:
    """DTO for category responses."""

    id: UUID
    name: str
    description: Optional[str]
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
