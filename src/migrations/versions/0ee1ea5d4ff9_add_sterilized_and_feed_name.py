"""add sterilized and feed name

Revision ID: 0ee1ea5d4ff9
Revises: a261ffdda0a9
Create Date: 2024-11-26 16:33:55.818273

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0ee1ea5d4ff9"
down_revision: Union[str, None] = "a261ffdda0a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "passwords", ["password_hash"])
    op.create_unique_constraint(None, "passwords", ["login"])
    op.add_column("pets", sa.Column("sterilized", sa.Boolean(), nullable=True))
    op.drop_column("pets_diseases", "disease_id")
    op.add_column(
        "pets_feeds", sa.Column("feed_name", sa.String(), nullable=True)
    )
    op.drop_column("pets_feeds", "feed_id")
    op.create_unique_constraint(None, "promos", ["promo"])
    op.create_unique_constraint(None, "users", ["mail"])
    op.create_unique_constraint(None, "users", ["tabel_number"])
    op.create_unique_constraint(None, "users", ["phone_number"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="unique")
    op.drop_constraint(None, "users", type_="unique")
    op.drop_constraint(None, "users", type_="unique")
    op.drop_constraint(None, "promos", type_="unique")
    op.add_column(
        "pets_feeds",
        sa.Column("feed_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.drop_column("pets_feeds", "feed_name")
    op.add_column(
        "pets_diseases",
        sa.Column(
            "disease_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.drop_column("pets", "sterilized")
    op.drop_constraint(None, "passwords", type_="unique")
    op.drop_constraint(None, "passwords", type_="unique")
    # ### end Alembic commands ###
