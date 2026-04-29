"""Use sqlalchemy-file (JSON) for agency.logo_url, partner.logo_url, building.image_url

Revision ID: h1i2j3k4l5m6
Revises: g2h3i4j5k6l7
Create Date: 2026-04-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'h1i2j3k4l5m6'
down_revision: Union[str, Sequence[str], None] = 'g2h3i4j5k6l7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # agency.logo_url : TEXT → JSON
    op.drop_column('agency', 'logo_url')
    op.add_column('agency', sa.Column('logo_url', sa.JSON(), nullable=True))

    # partner.logo_url : TEXT → JSON
    op.drop_column('partner', 'logo_url')
    op.add_column('partner', sa.Column('logo_url', sa.JSON(), nullable=True))

    # building.image_url : TEXT → JSON
    op.drop_column('building', 'image_url')
    op.add_column('building', sa.Column('image_url', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('building', 'image_url')
    op.add_column('building', sa.Column('image_url', sa.Text(), nullable=True))

    op.drop_column('partner', 'logo_url')
    op.add_column('partner', sa.Column('logo_url', sa.Text(), nullable=True))

    op.drop_column('agency', 'logo_url')
    op.add_column('agency', sa.Column('logo_url', sa.Text(), nullable=True))
