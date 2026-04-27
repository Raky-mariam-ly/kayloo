"""Shrink gender column VARCHAR(10) → VARCHAR(1) after normalization to M/F

Revision ID: e7f8a9b0c1d2
Revises: g2h3i4j5k6l7
Create Date: 2026-04-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e7f8a9b0c1d2'
down_revision: Union[str, Sequence[str], None] = 'g2h3i4j5k6l7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Toutes les valeurs sont déjà M ou F — on peut rétrécir sans perte
    op.alter_column(
        'user', 'gender',
        existing_type=sa.String(10),
        type_=sa.String(1),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'user', 'gender',
        existing_type=sa.String(1),
        type_=sa.String(10),
        existing_nullable=True,
    )
