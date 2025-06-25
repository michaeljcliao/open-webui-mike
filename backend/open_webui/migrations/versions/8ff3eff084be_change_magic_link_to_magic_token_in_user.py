"""change magic_link to magic_token in user

Revision ID: 8ff3eff084be
Revises: 3a63047004bf
Create Date: 2025-06-24 15:30:08.508666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '8ff3eff084be'
down_revision: Union[str, None] = '3a63047004bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        # SQLite: use batch_alter_table to rename
        with op.batch_alter_table("user") as batch:
            batch.alter_column(
                "magic_link",
                new_column_name="magic_token",
                existing_type=sa.String(),
            )
            batch.drop_constraint("uq_user_magic_link", type_="unique")
            batch.create_unique_constraint("uq_user_magic_token", ["magic_token"])
    else:
        # other DBs: true ALTER
        op.alter_column(
            "user",
            "magic_link",
            new_column_name="magic_token",
            existing_type=sa.String(),
        )
        op.drop_constraint("uq_user_magic_link", "user", type_="unique")
        op.create_unique_constraint("uq_user_magic_token", "user", ["magic_token"])


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("user") as batch:
            batch.drop_constraint("uq_user_magic_token", type_="unique")
            batch.alter_column(
                "magic_token",
                new_column_name="magic_link",
                existing_type=sa.String(),
            )
            batch.create_unique_constraint("uq_user_magic_link", ["magic_link"])
    else:
        op.drop_constraint("uq_user_magic_token", "user", type_="unique")
        op.alter_column(
            "user",
            "magic_token",
            new_column_name="magic_link",
            existing_type=sa.String(),
        )
        op.create_unique_constraint("uq_user_magic_link", "user", ["magic_link"])
