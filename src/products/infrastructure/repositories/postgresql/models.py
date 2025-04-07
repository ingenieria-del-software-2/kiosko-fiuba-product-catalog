"""SQLAlchemy ORM models for PostgreSQL repositories."""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.shared.database.base import Base


class BrandModel(Base):
    """SQLAlchemy model for brands table."""

    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    logo = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    products = relationship("ProductModel", back_populates="brand")


class CategoryModel(Base):
    """SQLAlchemy model for categories table."""

    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Self-referential relationship
    children = relationship(
        "CategoryModel",
        backref="parent",
        remote_side=[id],
        cascade="all",
        single_parent=True,
    )

    # Many-to-many relationship with products
    products = relationship(
        "ProductModel",
        secondary="product_categories",
        back_populates="categories",
    )


# Association table for product-category many-to-many relationship
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column(
        "product_id",
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ProductModel(Base):
    """SQLAlchemy model for products table."""

    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    price_amount = Column(Numeric(10, 2), nullable=False)
    price_currency = Column(String(3), nullable=False, default="USD")
    compare_at_price = Column(Numeric(10, 2), nullable=True)
    brand_id = Column(
        UUID(as_uuid=True),
        ForeignKey("brands.id", ondelete="SET NULL"),
        nullable=True,
    )
    model = Column(String(255), nullable=True)
    sku = Column(String(100), nullable=False, unique=True)
    status = Column(String(50), nullable=False, default="active")
    stock = Column(Integer, nullable=False, default=0)
    is_available = Column(Boolean, nullable=False, default=True)
    is_new = Column(Boolean, nullable=False, default=False)
    is_refurbished = Column(Boolean, nullable=False, default=False)
    condition = Column(String(50), nullable=False, default="new")
    has_variants = Column(Boolean, nullable=False, default=False)
    tags = Column(JSON, nullable=False, default=[])
    attributes = Column(JSON, nullable=False, default={})
    highlighted_features = Column(JSON, nullable=False, default=[])
    warranty = Column(JSON, nullable=True)
    shipping = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    brand = relationship("BrandModel", back_populates="products")
    images = relationship(
        "ProductImageModel", back_populates="product", cascade="all, delete-orphan"
    )
    variants = relationship(
        "ProductVariantModel",
        back_populates="parent_product",
        cascade="all, delete-orphan",
    )
    reviews = relationship(
        "ProductReviewModel", back_populates="product", cascade="all, delete-orphan"
    )
    categories = relationship(
        "CategoryModel",
        secondary="product_categories",
        back_populates="products",
    )
    config_options = relationship(
        "ConfigOptionModel", back_populates="product", cascade="all, delete-orphan"
    )
    promotions = relationship(
        "PromotionModel",
        secondary="product_promotions",
        back_populates="products",
    )


class ProductImageModel(Base):
    """SQLAlchemy model for product images table."""

    __tablename__ = "product_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    variant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=True,
    )
    url = Column(String(512), nullable=False)
    alt = Column(String(255), nullable=True)
    is_main = Column(Boolean, nullable=False, default=False)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    product = relationship("ProductModel", back_populates="images")
    variant = relationship("ProductVariantModel", back_populates="images")


class ProductVariantModel(Base):
    """SQLAlchemy model for product variants table."""

    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False, unique=True)
    price_amount = Column(Numeric(10, 2), nullable=False)
    price_currency = Column(String(3), nullable=False, default="USD")
    compare_at_price = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    is_available = Column(Boolean, nullable=False, default=True)
    is_selected = Column(Boolean, nullable=False, default=False)
    attributes = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    parent_product = relationship("ProductModel", back_populates="variants")
    images = relationship("ProductImageModel", back_populates="variant")


class ConfigOptionModel(Base):
    """SQLAlchemy model for product configuration options table."""

    __tablename__ = "config_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    values = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    product = relationship("ProductModel", back_populates="config_options")


class ProductReviewModel(Base):
    """SQLAlchemy model for product reviews table."""

    __tablename__ = "product_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(String(100), nullable=False)
    user_name = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    comment = Column(Text, nullable=False)
    is_verified_purchase = Column(Boolean, nullable=False, default=False)
    likes = Column(Integer, nullable=False, default=0)
    attributes = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    product = relationship("ProductModel", back_populates="reviews")


class SellerModel(Base):
    """SQLAlchemy model for sellers table."""

    __tablename__ = "sellers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    is_official = Column(Boolean, nullable=False, default=False)
    reputation = Column(JSON, nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class PromotionModel(Base):
    """SQLAlchemy model for promotions table."""

    __tablename__ = "promotions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    discount_percentage = Column(Float, nullable=True)
    discount_amount = Column(Numeric(10, 2), nullable=True)
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    products = relationship(
        "ProductModel",
        secondary="product_promotions",
        back_populates="promotions",
    )


# Association table for product-promotion many-to-many relationship
product_promotions = Table(
    "product_promotions",
    Base.metadata,
    Column(
        "product_id",
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "promotion_id",
        UUID(as_uuid=True),
        ForeignKey("promotions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class InventoryModel(Base):
    """SQLAlchemy model for inventory table."""

    __tablename__ = "inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    quantity = Column(Numeric(10, 0), nullable=False, default=0)
    status = Column(String(50), nullable=False, default="out_of_stock")
    reorder_threshold = Column(Numeric(10, 0), nullable=True)
    reorder_quantity = Column(Numeric(10, 0), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
