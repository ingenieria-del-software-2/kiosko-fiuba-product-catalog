"""Product Data Transfer Objects."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union
from uuid import UUID


@dataclass
class ProductCreateDTO:
    """DTO for creating a new product."""

    name: str
    description: str
    price: Decimal
    sku: str
    category_id: UUID
    currency: str = "USD"
    images: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    attributes: Dict[str, Union[str, int, float, bool]] = field(default_factory=dict)


@dataclass
class ProductUpdateDTO:
    """DTO for updating an existing product."""

    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    category_id: Optional[UUID] = None
    sku: Optional[str] = None
    status: Optional[str] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Union[str, int, float, bool]]] = None


@dataclass
class ProductResponseDTO:
    """DTO for product responses."""

    id: UUID
    name: str
    description: str
    price: Decimal
    currency: str
    category_id: UUID
    sku: str
    status: str
    images: List[str]
    tags: List[str]
    attributes: Dict[str, Union[str, int, float, bool]]
    created_at: datetime
    updated_at: datetime
