"""Widen gender column VARCHAR(1) → VARCHAR(10) and normalize male/female → M/F

Revision ID: d1e2f3a4b5c6
Revises: f8a9b0c1d2e3
Create Date: 2026-04-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Élargir la colonne avant la normalisation des données
    op.alter_column(
        'user', 'gender',
        existing_type=sa.String(1),
        type_=sa.String(10),
        existing_nullable=True,
    )
    # Normaliser les valeurs longues vers les codes à 1 caractère
    op.execute("UPDATE \"user\" SET gender = 'M' WHERE gender IN ('male', 'Male', 'MALE')")
    op.execute("UPDATE \"user\" SET gender = 'F' WHERE gender IN ('female', 'Female', 'FEMALE')")


def downgrade() -> None:
    # Reconvertir avant de rétrécir (évite la troncature)
    op.execute("UPDATE \"user\" SET gender = 'M' WHERE gender NOT IN ('M', 'F') AND gender ILIKE 'm%'")
    op.execute("UPDATE \"user\" SET gender = 'F' WHERE gender NOT IN ('M', 'F') AND gender ILIKE 'f%'")
    op.alter_column(
        'user', 'gender',
        existing_type=sa.String(10),
        type_=sa.String(1),
        existing_nullable=True,
    )
