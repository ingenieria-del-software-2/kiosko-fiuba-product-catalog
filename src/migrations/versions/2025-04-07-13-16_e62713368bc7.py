"""merge populate_slugs and e3bbdc30424c.

Revision ID: e62713368bc7
Revises: e3bbdc30424c, populate_slugs, modified_e3bbdc30424c, final_tables
Create Date: 2025-04-07 13:16:37.476955

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "e62713368bc7"
down_revision: Union[str, None] = (
    "e3bbdc30424c",
    "populate_slugs",
    "modified_e3bbdc30424c",
    "final_tables",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Run the migration."""
    pass


def downgrade() -> None:
    """Undo the migration."""
    pass
