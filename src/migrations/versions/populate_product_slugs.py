"""populate_product_slugs.

Revision ID: populate_product_slugs
Revises: populate_slugs
Create Date: 2025-04-07 14:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from slugify import slugify

# revision identifiers, used by Alembic.
revision: str = "populate_product_slugs"
down_revision: Union[str, None] = "populate_slugs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Run the migration."""
    # First, add the slug column as nullable
    op.add_column("products", sa.Column("slug", sa.String(255), nullable=True))

    # Get connection
    connection = op.get_bind()

    # Get all product names
    products = connection.execute(sa.text("SELECT id, name FROM products")).fetchall()

    # Keep track of existing slugs to avoid duplicates
    existing_slugs = set()

    # Update products with slugs
    for product_id, name in products:
        base_slug = slugify(name)
        slug = base_slug

        # If slug already exists, add counter until we find a unique one
        counter = 1
        while slug in existing_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1

        existing_slugs.add(slug)

        connection.execute(
            sa.text("UPDATE products SET slug = :slug WHERE id = :id"),
            {"slug": slug, "id": product_id},
        )

    # Now make the slug column non-nullable and unique
    op.alter_column("products", "slug", nullable=False)
    op.create_unique_constraint("uq_products_slug", "products", ["slug"])


def downgrade() -> None:
    """Remove the slug column."""
    op.drop_constraint("uq_products_slug", "products", type_="unique")
    op.drop_column("products", "slug")
