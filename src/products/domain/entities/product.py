"""Product domain entity."""

import uuid
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Brand(BaseModel):
    """Brand entity."""

    id: uuid.UUID
    name: str
    logo: Optional[str] = None


class Category(BaseModel):
    """Category entity."""

    id: uuid.UUID
    name: str
    slug: str
    parent_id: Optional[uuid.UUID] = None


class Image(BaseModel):
    """Image entity."""

    id: str
    url: str
    alt: Optional[str] = None
    is_main: bool = False
    order: int = 0


class ProductVariant(BaseModel):
    """Product variant entity."""

    id: uuid.UUID
    sku: str
    name: str
    price: float
    compare_at_price: Optional[float] = None
    attributes: Dict[str, Any]
    stock: int
    is_available: bool = True
    is_selected: bool = False
    image: Optional[str] = None
    images: Optional[List[Image]] = None


class ConfigOptionValue(BaseModel):
    """Configuration option value."""

    id: str
    value: str
    is_available: bool = True
    is_selected: bool = False
    image: Optional[str] = None


class ConfigOption(BaseModel):
    """Configuration option."""

    id: str
    name: str
    values: List[ConfigOptionValue]


class ShippingMethod(BaseModel):
    """Shipping method entity."""

    id: str
    name: str
    cost: float
    estimated_delivery_time: Dict[str, Any]


class Shipping(BaseModel):
    """Shipping information."""

    is_free: bool = False
    estimated_delivery_time: Dict[str, Any]
    available_shipping_methods: List[ShippingMethod]


class Warranty(BaseModel):
    """Warranty information."""

    has_warranty: bool = False
    length: Optional[int] = None
    unit: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None


class Review(BaseModel):
    """Product review."""

    id: str
    user_id: str
    user_name: str
    rating: int
    title: Optional[str] = None
    comment: str
    date: Union[datetime, str]
    is_verified_purchase: bool = False
    likes: int = 0
    attributes: Optional[List[Dict[str, Any]]] = None


class Product(BaseModel):
    """Product domain entity."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    slug: str
    description: str
    summary: Optional[str] = None
    price: float
    compare_at_price: Optional[float] = None
    currency: str = "ARS"
    brand: Optional[Brand] = None
    model: Optional[str] = None
    sku: str
    stock: int = 0
    is_available: bool = True
    is_new: bool = False
    is_refurbished: bool = False
    condition: str = "new"
    categories: List[Category] = []
    tags: List[str] = []
    images: List[Union[Image, Dict[str, Any]]] = []
    attributes: List[Dict[str, Any]] = []
    has_variants: bool = False
    variants: Optional[List[Union[ProductVariant, Dict[str, Any]]]] = None
    config_options: Optional[List[Union[ConfigOption, Dict[str, Any]]]] = None
    shipping: Optional[Union[Shipping, Dict[str, Any]]] = None
    warranty: Optional[Union[Warranty, Dict[str, Any]]] = None
    reviews: Optional[List[Union[Review, Dict[str, Any]]]] = None
    highlighted_features: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True
        json_encoders: ClassVar[Dict[type, Any]] = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat(),
        }
