"""final_tables.

Revision ID: final_tables
Revises: populate_product_defaults
Create Date: 2025-04-07 14:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "final_tables"
down_revision: Union[str, None] = "populate_product_defaults"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Run the final migration."""
    # Create the additional tables
    op.create_table(
        "brands",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("logo", sa.String(length=512), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "promotions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("discount_percentage", sa.Float(), nullable=True),
        sa.Column("discount_amount", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("valid_from", sa.DateTime(), nullable=False),
        sa.Column("valid_to", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sellers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_official", sa.Boolean(), nullable=False),
        sa.Column("reputation", sa.JSON(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Add remaining columns to products
    op.add_column("products", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column(
        "products",
        sa.Column("compare_at_price", sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.add_column("products", sa.Column("brand_id", sa.UUID(), nullable=True))
    op.add_column("products", sa.Column("model", sa.String(length=255), nullable=True))
    op.add_column("products", sa.Column("warranty", sa.JSON(), nullable=True))
    op.add_column("products", sa.Column("shipping", sa.JSON(), nullable=True))

    # Add foreign key
    op.create_foreign_key(
        "fk_products_brand_id",
        "products",
        "brands",
        ["brand_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Create many-to-many relationships
    op.create_table(
        "product_categories",
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("product_id", "category_id"),
    )

    op.create_table(
        "product_images",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("alt", sa.String(length=255), nullable=True),
        sa.Column("is_main", sa.Boolean(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "product_promotions",
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("promotion_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["promotion_id"],
            ["promotions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("product_id", "promotion_id"),
    )

    op.create_table(
        "product_reviews",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("user_name", sa.String(length=255), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("is_verified_purchase", sa.Boolean(), nullable=False),
        sa.Column("likes", sa.Integer(), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "product_variants",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("parent_product_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("price_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("price_currency", sa.String(length=3), nullable=False),
        sa.Column("compare_at_price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("is_selected", sa.Boolean(), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
    )

    op.create_table(
        "config_options",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("values", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Drop old category reference and images column
    op.drop_constraint("products_category_id_fkey", "products", type_="foreignkey")
    op.drop_column("products", "category_id")
    op.drop_column("products", "images")

    # Drop category name unique constraint since we have slug as unique identifier now
    op.drop_constraint("categories_name_key", "categories", type_="unique")


def downgrade() -> None:
    """Revert the migration."""
    # Restore category name unique constraint
    op.create_unique_constraint("categories_name_key", "categories", ["name"])

    # Restore old columns
    op.add_column(
        "products",
        sa.Column("images", sa.JSON(), nullable=False),
    )
    op.add_column(
        "products",
        sa.Column("category_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "products_category_id_fkey",
        "products",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Drop the tables
    op.drop_table("config_options")
    op.drop_table("product_variants")
    op.drop_table("product_reviews")
    op.drop_table("product_promotions")
    op.drop_table("product_images")
    op.drop_table("product_categories")

    # Drop foreign key
    op.drop_constraint("fk_products_brand_id", "products", type_="foreignkey")

    # Drop remaining columns
    op.drop_column("products", "shipping")
    op.drop_column("products", "warranty")
    op.drop_column("products", "model")
    op.drop_column("products", "brand_id")
    op.drop_column("products", "compare_at_price")
    op.drop_column("products", "summary")

    # Drop tables
    op.drop_table("sellers")
    op.drop_table("promotions")
    op.drop_table("brands")
