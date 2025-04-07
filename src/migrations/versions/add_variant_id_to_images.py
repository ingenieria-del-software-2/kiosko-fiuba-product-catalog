"""Add variant_id to product_images.

Revision ID: add_variant_id_to_images
Revises: e62713368bc7
Create Date: 2023-07-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "add_variant_id_to_images"
down_revision: Union[str, None] = "e62713368bc7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add variant_id column to product_images table."""
    op.add_column(
        "product_images",
        sa.Column(
            "variant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("product_variants.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove variant_id column from product_images table."""
    op.drop_column("product_images", "variant_id")
