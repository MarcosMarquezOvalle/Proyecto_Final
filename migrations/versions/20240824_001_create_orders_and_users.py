"""create orders and users tables

Revision ID: 20240824_001
Revises:
Create Date: 2024-08-24 16:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20240824_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("username"),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("items_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'admin123')")


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_table("users")
