"""Add property_gallery table for inline gallery images

Revision ID: c1d2e3f4a5b6
Revises: b4c5d6e7f8a9
Create Date: 2026-04-20 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'b4c5d6e7f8a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'property_gallery',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('property_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ['property_id'], ['property_property.id'],
            name='fk__property_gallery__property_id',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('property_id', name='uq__property_gallery__property_id'),
    )


def downgrade() -> None:
    op.drop_table('property_gallery')
