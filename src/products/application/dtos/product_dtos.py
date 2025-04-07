"""Product DTO classes for the application layer."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductCreateDTO(BaseModel):
    """DTO for creating a new product."""

    name: str
    description: str
    price: float
    currency: str = "USD"
    category_id: UUID
    sku: str
    status: str = "active"
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ProductUpdateDTO(BaseModel):
    """DTO for updating a product."""

    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    category_id: Optional[UUID] = None
    sku: Optional[str] = None
    status: Optional[str] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None


class ProductResponseDTO(BaseModel):
    """DTO for product response."""

    id: UUID
    name: str
    description: str
    price: float
    currency: str
    category_id: UUID
    sku: str
    status: str
    images: List[str]
    tags: List[str]
    attributes: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
