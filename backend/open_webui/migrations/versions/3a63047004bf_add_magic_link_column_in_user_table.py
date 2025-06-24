"""Add magic_link column in user table

Revision ID: 3a63047004bf
Revises: 3781e22d8b01
Create Date: 2025-06-24 00:39:06.903618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '3a63047004bf'
down_revision: Union[str, None] = '3781e22d8b01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        # SQLite needs a table copy for ALTERs
        with op.batch_alter_table("user") as batch:
            batch.add_column(sa.Column("magic_link", sa.String(), nullable=True))
            batch.create_unique_constraint("uq_user_magic_link", ["magic_link"])
    else:
        # other DBs can do it in‐place
        op.add_column(
            "user",
            sa.Column("magic_link", sa.String(), nullable=True),
        )
        op.create_unique_constraint(
            "uq_user_magic_link",
            "user",
            ["magic_link"],
        )

def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("user") as batch:
            batch.drop_constraint("uq_user_magic_link", type_="unique")
            batch.drop_column("magic_link")
    else:
        op.drop_constraint("uq_user_magic_link", "user", type_="unique")
        op.drop_column("user", "magic_link")
