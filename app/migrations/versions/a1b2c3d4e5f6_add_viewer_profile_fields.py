"""Add viewer profile fields (office_phone, whatsapp_number, company_name, address)

Revision ID: a1b2c3d4e5f6
Revises: f8a9b0c1d2e3
Create Date: 2026-04-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f8a9b0c1d2e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('office_phone', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('whatsapp_number', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('company_name', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('address', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'address')
    op.drop_column('user', 'company_name')
    op.drop_column('user', 'whatsapp_number')
    op.drop_column('user', 'office_phone')
