"""populate_slugs.

Revision ID: populate_slugs
Revises: manual_convert
Create Date: 2025-04-07 14:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from slugify import slugify

# revision identifiers, used by Alembic.
revision: str = "populate_slugs"
down_revision: Union[str, None] = "manual_convert"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Run the migration."""
    # First, add the slug column as nullable
    op.add_column("categories", sa.Column("slug", sa.String(255), nullable=True))

    # Get connection
    connection = op.get_bind()

    # Get all category names
    categories = connection.execute(
        sa.text("SELECT id, name FROM categories")
    ).fetchall()

    # Update categories with slugs
    for category_id, name in categories:
        slug = slugify(name)
        connection.execute(
            sa.text("UPDATE categories SET slug = :slug WHERE id = :id"),
            {"slug": slug, "id": category_id},
        )

    # Now make the slug column non-nullable and unique
    op.alter_column("categories", "slug", nullable=False)
    op.create_unique_constraint("uq_categories_slug", "categories", ["slug"])


def downgrade() -> None:
    """Remove the slug column."""
    op.drop_constraint("uq_categories_slug", "categories", type_="unique")
    op.drop_column("categories", "slug")
