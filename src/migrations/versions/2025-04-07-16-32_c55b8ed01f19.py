"""initial_migration.

Revision ID: c55b8ed01f19
Revises: 407525e30225
Create Date: 2025-04-07 16:32:22.949971

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "c55b8ed01f19"
down_revision: Union[str, None] = "407525e30225"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Run the migration."""
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###


def downgrade() -> None:
    """Undo the migration."""
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###
