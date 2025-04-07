"""populate_product_defaults.

Revision ID: populate_product_defaults
Revises: populate_product_slugs
Create Date: 2025-04-07 14:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "populate_product_defaults"
down_revision: Union[str, None] = "populate_product_slugs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Run the migration to add default values to existing products."""
    # First add columns as nullable
    op.add_column("products", sa.Column("stock", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("is_available", sa.Boolean(), nullable=True))
    op.add_column("products", sa.Column("is_new", sa.Boolean(), nullable=True))
    op.add_column("products", sa.Column("is_refurbished", sa.Boolean(), nullable=True))
    op.add_column(
        "products", sa.Column("condition", sa.String(length=50), nullable=True)
    )
    op.add_column("products", sa.Column("has_variants", sa.Boolean(), nullable=True))
    op.add_column(
        "products", sa.Column("highlighted_features", sa.JSON(), nullable=True)
    )

    # Get connection
    connection = op.get_bind()

    # Update existing products with default values
    connection.execute(
        sa.text(
            """
        UPDATE products SET
            stock = 100,
            is_available = true,
            is_new = true,
            is_refurbished = false,
            condition = 'new',
            has_variants = false,
            highlighted_features = '[]'::jsonb
    """
        )
    )

    # Now make columns not nullable
    op.alter_column("products", "stock", nullable=False)
    op.alter_column("products", "is_available", nullable=False)
    op.alter_column("products", "is_new", nullable=False)
    op.alter_column("products", "is_refurbished", nullable=False)
    op.alter_column("products", "condition", nullable=False)
    op.alter_column("products", "has_variants", nullable=False)
    op.alter_column("products", "highlighted_features", nullable=False)


def downgrade() -> None:
    """Remove the added columns."""
    op.drop_column("products", "highlighted_features")
    op.drop_column("products", "has_variants")
    op.drop_column("products", "condition")
    op.drop_column("products", "is_refurbished")
    op.drop_column("products", "is_new")
    op.drop_column("products", "is_available")
    op.drop_column("products", "stock")
