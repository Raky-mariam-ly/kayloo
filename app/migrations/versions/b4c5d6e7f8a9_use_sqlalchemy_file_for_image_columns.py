"""Use sqlalchemy-file (JSON) for image columns: property.image_url and property_image.url

Revision ID: b4c5d6e7f8a9
Revises: a3b1c2d4e5f6
Create Date: 2026-04-20 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b4c5d6e7f8a9'
down_revision: Union[str, Sequence[str], None] = 'a3b1c2d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # property_image.url : TEXT → JSONB
    # Les données existantes (URLs texte) sont perdues — migration de rupture volontaire.
    op.drop_column('property_image', 'url')
    op.add_column('property_image', sa.Column('url', sa.JSON(), nullable=False,
                                              server_default='{}'))
    op.alter_column('property_image', 'url', server_default=None)

    # property_property.image_url : TEXT → JSONB
    op.drop_column('property_property', 'image_url')
    op.add_column('property_property', sa.Column('image_url', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('property_property', 'image_url')
    op.add_column('property_property', sa.Column('image_url', sa.Text(), nullable=True))

    op.drop_column('property_image', 'url')
    op.add_column('property_image', sa.Column('url', sa.Text(), nullable=False,
                                              server_default=''))
    op.alter_column('property_image', 'url', server_default=None)
