"""Data Transfer Objects (DTOs) for the product domain."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Callable, ClassVar

from pydantic import BaseModel, RootModel, validator


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
    parentId: Optional[uuid.UUID] = None


class ImageDTO(BaseModel):
    """DTO for product image."""

    id: str
    url: str
    alt: Optional[str] = None
    isMain: bool = False
    order: int = 0


class AttributeDTO(BaseModel):
    """DTO for product attribute."""

    id: str
    name: str
    value: Any
    displayValue: str
    isHighlighted: bool = False
    groupName: Optional[str] = None


class ConfigOptionValueDTO(BaseModel):
    """DTO for config option value."""

    id: str
    value: str
    isAvailable: bool = True
    isSelected: bool = False
    image: Optional[str] = None


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
    estimatedDeliveryTime: Dict[str, Any]


class ShippingDTO(BaseModel):
    """DTO for product shipping information."""

    isFree: bool = False
    estimatedDeliveryTime: Dict[str, Any]
    availableShippingMethods: List[ShippingMethodDTO]


class SellerReputationDTO(BaseModel):
    """DTO for seller reputation."""

    level: str
    score: float
    totalSales: int
    completedSales: int
    canceledSales: int
    totalReviews: int


class SellerDTO(BaseModel):
    """DTO for product seller."""

    id: str
    name: str
    isOfficial: bool = False
    reputation: Optional[SellerReputationDTO] = None
    location: Optional[str] = None


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
    userId: str
    userName: str
    rating: int
    title: Optional[str] = None
    comment: str
    date: datetime
    isVerifiedPurchase: bool = False
    likes: int = 0
    attributes: Optional[List[ReviewAttributeDTO]] = None


class InstallmentDTO(BaseModel):
    """DTO for payment installment."""

    quantity: int
    amount: float
    interestRate: float
    totalAmount: float


class PaymentOptionDTO(BaseModel):
    """DTO for payment option."""

    id: str
    type: str
    name: str
    installments: List[InstallmentDTO]


class WarrantyDTO(BaseModel):
    """DTO for product warranty."""

    hasWarranty: bool = False
    length: Optional[int] = None
    unit: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None


class PromotionDTO(BaseModel):
    """DTO for product promotion."""

    id: str
    type: str
    description: str
    discountPercentage: Optional[float] = None
    validFrom: datetime
    validTo: datetime


class ProductVariantDTO(BaseModel):
    """DTO for product variant."""

    id: uuid.UUID
    sku: str
    name: str
    price: float
    compareAtPrice: Optional[float] = None
    attributes: Dict[str, Any]
    stock: int
    isAvailable: bool = True
    isSelected: bool = False
    image: Optional[str] = None
    images: Optional[List[ImageDTO]] = None


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
    compareAtPrice: Optional[float] = None
    currency: str = "ARS"
    stock: int = 0
    isAvailable: bool = True
    isNew: bool = False
    isRefurbished: bool = False
    condition: str = "new"
    categories: List[CategoryDTO] = []
    tags: List[str] = []
    images: List[ImageDTO] = []
    attributes: List[AttributeDTO] = []
    hasVariants: bool = False
    variants: Optional[List[ProductVariantDTO]] = None
    configOptions: Optional[List[ConfigOptionDTO]] = None
    shipping: Optional[ShippingDTO] = None
    seller: Optional[SellerDTO] = None
    rating: Optional[RatingDTO] = None
    reviews: Optional[List[ReviewDTO]] = None
    paymentOptions: Optional[List[PaymentOptionDTO]] = None
    warranty: Optional[WarrantyDTO] = None
    promotions: Optional[List[PromotionDTO]] = None
    highlightedFeatures: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class ProductCreateDTO(BaseModel):
    """DTO for product creation."""

    name: str
    slug: Optional[str] = None
    description: str
    summary: Optional[str] = None
    price: float
    compareAtPrice: Optional[float] = None
    currency: str = "ARS"
    brand_id: Optional[uuid.UUID] = None
    model: Optional[str] = None
    sku: str
    stock: int = 0
    isAvailable: bool = True
    isNew: bool = False
    isRefurbished: bool = False
    condition: str = "new"
    category_ids: List[uuid.UUID] = []
    tags: List[str] = []
    images: List[Dict[str, Any]] = []
    attributes: List[Dict[str, Any]] = []
    hasVariants: bool = False
    variants: Optional[List[Dict[str, Any]]] = None
    configOptions: Optional[List[Dict[str, Any]]] = None
    shipping: Optional[Dict[str, Any]] = None
    seller_id: Optional[str] = None
    warranty: Optional[Dict[str, Any]] = None
    highlightedFeatures: Optional[List[str]] = None

    @validator("slug", pre=True, always=True)
    def set_slug(self, v: Optional[str], values: Dict[str, Any]) -> str:
        """Set slug from name if not provided."""
        if not v and "name" in values:
            from slugify import slugify
            return str(slugify(values["name"]))
        return v if v is not None else ""


class ProductUpdateDTO(BaseModel):
    """DTO for product update."""

    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    price: Optional[float] = None
    compareAtPrice: Optional[float] = None
    compare_at_price: Optional[float] = None
    currency: Optional[str] = None
    brand_id: Optional[uuid.UUID] = None
    model: Optional[str] = None
    sku: Optional[str] = None
    stock: Optional[int] = None
    isAvailable: Optional[bool] = None
    is_available: Optional[bool] = None
    isNew: Optional[bool] = None
    is_new: Optional[bool] = None
    isRefurbished: Optional[bool] = None
    is_refurbished: Optional[bool] = None
    condition: Optional[str] = None
    category_ids: Optional[List[uuid.UUID]] = None
    tags: Optional[List[str]] = None
    images: Optional[List[Dict[str, Any]]] = None
    attributes: Optional[List[Dict[str, Any]]] = None
    hasVariants: Optional[bool] = None
    has_variants: Optional[bool] = None
    variants: Optional[List[Dict[str, Any]]] = None
    configOptions: Optional[List[Dict[str, Any]]] = None
    config_options: Optional[List[Dict[str, Any]]] = None
    shipping: Optional[Dict[str, Any]] = None
    seller_id: Optional[str] = None
    warranty: Optional[Dict[str, Any]] = None
    highlightedFeatures: Optional[List[str]] = None
    highlighted_features: Optional[List[str]] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True


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

    @validator("slug", pre=True, always=True)
    def set_slug(self, v: Optional[str], values: Dict[str, Any]) -> str:
        """Set slug from name if not provided."""
        if not v and "name" in values:
            from slugify import slugify
            return str(slugify(values["name"]))
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
