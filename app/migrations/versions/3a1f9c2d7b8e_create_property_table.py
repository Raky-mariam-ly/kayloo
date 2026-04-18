"""Create property_property table

Revision ID: 3a1f9c2d7b8e
Revises: c7ced9a51e91
Create Date: 2026-04-16 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a1f9c2d7b8e'
down_revision: Union[str, Sequence[str], None] = 'c7ced9a51e91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'property_property',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('building_id', sa.UUID(), nullable=True),
        sa.Column('owner_id', sa.UUID(), nullable=True),
        sa.Column('agency_id', sa.UUID(), nullable=True),
        sa.Column('label', sa.Text(), nullable=True),
        sa.Column('code', sa.Text(), nullable=True),
        sa.Column('status_before_reserved', sa.Text(), nullable=True),
        sa.Column('managed_by', sa.Text(), nullable=True),
        sa.Column('base_price_type', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sale_account_code', sa.Text(), nullable=True),
        sa.Column('usage', sa.Text(), nullable=True),
        sa.Column('type', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=True),
        sa.Column('rent_type', sa.Text(), nullable=True),
        sa.Column('rental_period', sa.Text(), nullable=True),
        sa.Column('tag', sa.Text(), nullable=True),
        sa.Column('main_picture_path', sa.Text(), nullable=True),
        sa.Column('level', sa.Text(), nullable=True),
        sa.Column('position', sa.Text(), nullable=True),
        sa.Column('apartment_number', sa.Text(), nullable=True),
        sa.Column('country', sa.Text(), nullable=True),
        sa.Column('city', sa.Text(), nullable=True),
        sa.Column('street', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('zone', sa.Text(), nullable=True),
        sa.Column('bath_room_count', sa.Integer(), nullable=True),
        sa.Column('bed_room_count', sa.Integer(), nullable=True),
        sa.Column('kitchen_count', sa.Integer(), nullable=True),
        sa.Column('living_room_count', sa.Integer(), nullable=True),
        sa.Column('build_year', sa.Text(), nullable=True),
        sa.Column('lng', sa.Numeric(21, 6), nullable=True),
        sa.Column('lat', sa.Numeric(21, 6), nullable=True),
        sa.Column('acquisition_date', sa.Date(), nullable=True),
        sa.Column('acquisition_price', sa.Numeric(21, 6), nullable=True),
        sa.Column('acquisition_fee', sa.Numeric(21, 6), nullable=True),
        sa.Column('surface', sa.Numeric(21, 6), nullable=True),
        sa.Column('free_since', sa.Date(), nullable=True),
        sa.Column('currency', sa.Text(), nullable=True),
        sa.Column('vat_rate', sa.Numeric(21, 6), nullable=True),
        sa.Column('tom_rate', sa.Numeric(21, 6), nullable=True),
        sa.Column('ir_rate', sa.Numeric(21, 6), nullable=True),
        sa.Column('mgmt_rate', sa.Numeric(21, 6), nullable=True),
        sa.Column('commission_rate', sa.Numeric(21, 6), nullable=True),
        sa.Column('deposit_rate', sa.Numeric(21, 6), nullable=True),
        sa.Column('sale_price', sa.Numeric(21, 6), nullable=True),
        sa.Column('price', sa.Numeric(21, 6), nullable=True),
        sa.Column('base_price', sa.Numeric(21, 6), nullable=True),
        sa.Column('extra_price', sa.Numeric(21, 6), nullable=True),
        sa.Column('rent_price', sa.Numeric(21, 6), nullable=True),
        sa.Column('syndic_amount', sa.Numeric(21, 6), nullable=True),
        sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_exposed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_saleable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_managed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('archived', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Text(), nullable=True),
        sa.Column('updated_by', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['agency_id'], ['agency.id'], name='fk__property_property__agency_id'),
        sa.ForeignKeyConstraint(['created_by'], ['user.email'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['user.email'], ),
        sa.PrimaryKeyConstraint('id', name='pk__property_property__id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('property_property')
