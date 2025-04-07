"""Database migrations for product tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID


def create_products_tables() -> None:
    """Create tables for the product catalog.

    This creates the following tables:
    - categories
    - products
    - inventory

    Each with appropriate indices and constraints.
    """
    # Create categories table
    op.create_table(
        "categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("parent_id", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["categories.id"],
            name="fk_category_parent",
            ondelete="SET NULL",
        ),
    )

    # Create index on category name for faster lookups
    op.create_index("ix_categories_name", "categories", ["name"])

    # Create products table
    op.create_table(
        "products",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("price_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("price_currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("category_id", UUID(as_uuid=True), nullable=True),
        sa.Column("sku", sa.String(100), nullable=False, unique=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("images", ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("tags", ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("attributes", JSON, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name="fk_product_category",
            ondelete="SET NULL",
        ),
    )

    # Create indices on products
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_sku", "products", ["sku"])
    op.create_index("ix_products_status", "products", ["status"])
    op.create_index("ix_products_tags", "products", ["tags"], postgresql_using="gin")

    # Create inventory table
    op.create_table(
        "inventory",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("quantity", sa.Numeric(10, 0), nullable=False, server_default="0"),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="out_of_stock",
        ),
        sa.Column("reorder_threshold", sa.Numeric(10, 0), nullable=True),
        sa.Column("reorder_quantity", sa.Numeric(10, 0), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_inventory_product",
            ondelete="CASCADE",
        ),
    )

    # Create indices on inventory
    op.create_index("ix_inventory_product_id", "inventory", ["product_id"])
    op.create_index("ix_inventory_status", "inventory", ["status"])


def drop_products_tables() -> None:
    """Drop all tables for the product catalog."""
    op.drop_table("inventory")
    op.drop_table("products")
    op.drop_table("categories")
