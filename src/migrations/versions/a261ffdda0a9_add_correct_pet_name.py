"""add_correct_pet_name

Revision ID: a261ffdda0a9
Revises: 78f624639305
Create Date: 2024-11-26 14:14:35.550124

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a261ffdda0a9"
down_revision: Union[str, None] = "abc30b993bfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pets", sa.Column("name", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("pets", "name")
