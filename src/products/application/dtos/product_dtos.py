"""Data Transfer Objects (DTOs) for the product domain."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, RootModel, ValidationInfo, field_validator


class BrandDTO(BaseModel):
    """DTO for product brand."""

    id: uuid.UUID
    name: str
    logo: Optional[str] = None


class CategoryDTO(BaseModel):
    """DTO for product category."""

    id: uuid.UUID
    name: str
    slug: str
    parent_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: (
            "parentId" if field_name == "parent_id" else field_name
        ),
    )


class ImageDTO(BaseModel):
    """DTO for product image."""

    id: str
    url: str
    alt: Optional[str] = None
    is_main: bool = False
    order: int = 0

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: (
            "isMain" if field_name == "is_main" else field_name
        ),
    )


class AttributeDTO(BaseModel):
    """DTO for product attribute."""

    id: str
    name: str
    value: Any
    display_value: str
    is_highlighted: bool = False
    group_name: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "display_value": "displayValue",
            "is_highlighted": "isHighlighted",
            "group_name": "groupName",
        }.get(field_name, field_name),
    )


class ConfigOptionValueDTO(BaseModel):
    """DTO for config option value."""

    id: str
    value: str
    is_available: bool = True
    is_selected: bool = False
    image: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "is_available": "isAvailable",
            "is_selected": "isSelected",
        }.get(field_name, field_name),
    )


class ConfigOptionDTO(BaseModel):
    """DTO for product configuration option."""

    id: str
    name: str
    values: List[ConfigOptionValueDTO]


class ShippingMethodDTO(BaseModel):
    """DTO for product shipping method."""

    id: str
    name: str
    cost: float
    estimated_delivery_time: Dict[str, Any]

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: (
            "estimatedDeliveryTime"
            if field_name == "estimated_delivery_time"
            else field_name
        ),
    )


class ShippingDTO(BaseModel):
    """DTO for product shipping information."""

    is_free: bool = False
    estimated_delivery_time: Dict[str, Any]
    available_shipping_methods: List[ShippingMethodDTO]

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "is_free": "isFree",
            "estimated_delivery_time": "estimatedDeliveryTime",
            "available_shipping_methods": "availableShippingMethods",
        }.get(field_name, field_name),
    )


class SellerReputationDTO(BaseModel):
    """DTO for seller reputation."""

    level: str
    score: float
    total_sales: int
    completed_sales: int
    canceled_sales: int
    total_reviews: int

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "total_sales": "totalSales",
            "completed_sales": "completedSales",
            "canceled_sales": "canceledSales",
            "total_reviews": "totalReviews",
        }.get(field_name, field_name),
    )


class SellerDTO(BaseModel):
    """DTO for product seller."""

    id: str
    name: str
    is_official: bool = False
    reputation: Optional[SellerReputationDTO] = None
    location: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: (
            "isOfficial" if field_name == "is_official" else field_name
        ),
    )


class RatingDistributionDTO(RootModel):
    """DTO for rating distribution."""

    root: Dict[str, int]

    @property
    def dict_values(self) -> Dict[str, int]:
        """Get the distribution as a dict."""
        return self.root


class RatingDTO(BaseModel):
    """DTO for product rating."""

    average: float
    count: int
    distribution: RatingDistributionDTO


class ReviewAttributeDTO(BaseModel):
    """DTO for review attribute."""

    name: str
    rating: int


class ReviewDTO(BaseModel):
    """DTO for product review."""

    id: str
    user_id: str
    user_name: str
    rating: int
    title: Optional[str] = None
    comment: str
    date: datetime
    is_verified_purchase: bool = False
    likes: int = 0
    attributes: Optional[List[ReviewAttributeDTO]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "user_id": "userId",
            "user_name": "userName",
            "is_verified_purchase": "isVerifiedPurchase",
        }.get(field_name, field_name),
    )


class InstallmentDTO(BaseModel):
    """DTO for payment installment."""

    quantity: int
    amount: float
    interest_rate: float
    total_amount: float

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "interest_rate": "interestRate",
            "total_amount": "totalAmount",
        }.get(field_name, field_name),
    )


class PaymentOptionDTO(BaseModel):
    """DTO for payment option."""

    id: str
    type: str
    name: str
    installments: List[InstallmentDTO]


class WarrantyDTO(BaseModel):
    """DTO for product warranty."""

    has_warranty: bool = False
    length: Optional[int] = None
    unit: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: (
            "hasWarranty" if field_name == "has_warranty" else field_name
        ),
    )


class PromotionDTO(BaseModel):
    """DTO for product promotion."""

    id: str
    type: str
    description: str
    discount_percentage: Optional[float] = None
    valid_from: datetime
    valid_to: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "discount_percentage": "discountPercentage",
            "valid_from": "validFrom",
            "valid_to": "validTo",
        }.get(field_name, field_name),
    )


class ProductVariantDTO(BaseModel):
    """DTO for product variant."""

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
    images: Optional[List[ImageDTO]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "compare_at_price": "compareAtPrice",
            "is_available": "isAvailable",
            "is_selected": "isSelected",
        }.get(field_name, field_name),
    )


class ProductResponseDTO(BaseModel):
    """DTO for product response."""

    id: uuid.UUID
    sku: str
    name: str
    slug: str
    description: str
    summary: Optional[str] = None
    brand: Optional[BrandDTO] = None
    model: Optional[str] = None
    price: float
    compare_at_price: Optional[float] = None
    currency: str = "ARS"
    stock: int = 0
    is_available: bool = True
    is_new: bool = False
    is_refurbished: bool = False
    condition: str = "new"
    categories: List[CategoryDTO] = []
    tags: List[str] = []
    images: List[ImageDTO] = []
    attributes: List[AttributeDTO] = []
    has_variants: bool = False
    variants: Optional[List[ProductVariantDTO]] = None
    config_options: Optional[List[ConfigOptionDTO]] = None
    shipping: Optional[ShippingDTO] = None
    seller: Optional[SellerDTO] = None
    rating: Optional[RatingDTO] = None
    reviews: Optional[List[ReviewDTO]] = None
    payment_options: Optional[List[PaymentOptionDTO]] = None
    warranty: Optional[WarrantyDTO] = None
    promotions: Optional[List[PromotionDTO]] = None
    highlighted_features: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "compare_at_price": "compareAtPrice",
            "is_available": "isAvailable",
            "is_new": "isNew",
            "is_refurbished": "isRefurbished",
            "has_variants": "hasVariants",
            "config_options": "configOptions",
            "payment_options": "paymentOptions",
            "highlighted_features": "highlightedFeatures",
        }.get(field_name, field_name),
    )

    @classmethod
    def model_serializer(cls, obj: "ProductResponseDTO") -> dict:
        """Custom serializer for the model."""
        data = obj.__dict__.copy()
        # Convert UUID to string
        if isinstance(data.get("id"), uuid.UUID):
            data["id"] = str(data["id"])
        # Convert datetime to ISO format
        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data["created_at"].isoformat()
        if isinstance(data.get("updated_at"), datetime):
            data["updated_at"] = data["updated_at"].isoformat()
        return data


class ProductCreateDTO(BaseModel):
    """DTO for product creation."""

    name: str
    slug: Optional[str] = None
    description: str
    summary: Optional[str] = None
    price: float
    compare_at_price: Optional[float] = None
    currency: str = "ARS"
    brand_id: Optional[uuid.UUID] = None
    model: Optional[str] = None
    sku: str
    stock: int = 0
    is_available: bool = True
    is_new: bool = False
    is_refurbished: bool = False
    condition: str = "new"
    category_ids: List[uuid.UUID] = []
    tags: List[str] = []
    images: List[Dict[str, Any]] = []
    attributes: List[Dict[str, Any]] = []
    has_variants: bool = False
    variants: Optional[List[Dict[str, Any]]] = None
    config_options: Optional[List[Dict[str, Any]]] = None
    shipping: Optional[Dict[str, Any]] = None
    seller_id: Optional[str] = None
    warranty: Optional[Dict[str, Any]] = None
    highlighted_features: Optional[List[str]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "compare_at_price": "compareAtPrice",
            "is_available": "isAvailable",
            "is_new": "isNew",
            "is_refurbished": "isRefurbished",
            "has_variants": "hasVariants",
            "config_options": "configOptions",
            "highlighted_features": "highlightedFeatures",
        }.get(field_name, field_name),
    )

    @field_validator("slug", mode="before")
    @classmethod
    def set_slug(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Set slug from name if not provided."""
        if not v and "name" in info.data:
            from python_slugify import slugify

            return str(slugify(info.data["name"]))
        return v if v is not None else ""


class ProductUpdateDTO(BaseModel):
    """DTO for product update."""

    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    currency: Optional[str] = None
    brand_id: Optional[uuid.UUID] = None
    model: Optional[str] = None
    sku: Optional[str] = None
    stock: Optional[int] = None
    is_available: Optional[bool] = None
    is_new: Optional[bool] = None
    is_refurbished: Optional[bool] = None
    condition: Optional[str] = None
    category_ids: Optional[List[uuid.UUID]] = None
    tags: Optional[List[str]] = None
    images: Optional[List[Dict[str, Any]]] = None
    attributes: Optional[List[Dict[str, Any]]] = None
    has_variants: Optional[bool] = None
    variants: Optional[List[Dict[str, Any]]] = None
    config_options: Optional[List[Dict[str, Any]]] = None
    shipping: Optional[Dict[str, Any]] = None
    seller_id: Optional[str] = None
    warranty: Optional[Dict[str, Any]] = None
    highlighted_features: Optional[List[str]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: {
            "compare_at_price": "compareAtPrice",
            "is_available": "isAvailable",
            "is_new": "isNew",
            "is_refurbished": "isRefurbished",
            "has_variants": "hasVariants",
            "config_options": "configOptions",
            "highlighted_features": "highlightedFeatures",
        }.get(field_name, field_name),
    )


class BrandCreateDTO(BaseModel):
    """DTO for brand creation."""

    name: str
    logo: Optional[str] = None
    description: Optional[str] = None


class BrandUpdateDTO(BaseModel):
    """DTO for brand update."""

    name: Optional[str] = None
    logo: Optional[str] = None
    description: Optional[str] = None


class CategoryCreateDTO(BaseModel):
    """DTO for category creation."""

    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None

    @field_validator("slug", mode="before")
    @classmethod
    def set_slug(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Set slug from name if not provided."""
        if not v and "name" in info.data:
            from python_slugify import slugify

            return str(slugify(info.data["name"]))
        return v if v is not None else ""


class CategoryUpdateDTO(BaseModel):
    """DTO for category update."""

    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None


class ProductFilterDTO(BaseModel):
    """DTO for product filtering."""

    category_id: Optional[uuid.UUID] = None
    brand_id: Optional[uuid.UUID] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    is_available: Optional[bool] = None
    is_new: Optional[bool] = None
    condition: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
    limit: Optional[int] = 10
    offset: Optional[int] = 0
