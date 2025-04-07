"""manually_convert_arrays_to_json.

Revision ID: manual_convert
Revises: d246a44e606e
Create Date: 2025-04-07 09:15:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "manual_convert"
down_revision: Union[str, None] = "d246a44e606e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Run the migration."""
    # Manual SQL with USING clause to properly convert arrays to JSON
    op.execute(
        "ALTER TABLE products ALTER COLUMN images TYPE JSON USING to_json(images)"
    )
    op.execute("ALTER TABLE products ALTER COLUMN tags TYPE JSON USING to_json(tags)")


def downgrade() -> None:
    """Undo the migration."""
    # Converting back would be more complex and likely require custom logic
    op.execute(
        "ALTER TABLE products ALTER COLUMN images TYPE VARCHAR[] USING ARRAY(SELECT jsonb_array_elements_text(to_jsonb(images)))"
    )
    op.execute(
        "ALTER TABLE products ALTER COLUMN tags TYPE VARCHAR[] USING ARRAY(SELECT jsonb_array_elements_text(to_jsonb(tags)))"
    )
