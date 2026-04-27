"""Merge CRM branch and main branch heads

Revision ID: f0a1b2c3d4e5
Revises: 198cbc5c5d42, e7f8a9b0c1d2
Create Date: 2026-04-27 00:00:00.000000

"""
from typing import Sequence, Union


revision: str = 'f0a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = ('198cbc5c5d42', 'e7f8a9b0c1d2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
