"""Fix property_property: add FK constraints for building_id/owner_id, change build_year to Integer

Revision ID: a3b1c2d4e5f6
Revises: 5151dd9cc13d
Create Date: 2026-04-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b1c2d4e5f6'
down_revision: Union[str, Sequence[str], None] = '5151dd9cc13d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les contraintes FK manquantes
    op.create_foreign_key(
        'fk__property_property__building_id',
        'property_property', 'building',
        ['building_id'], ['id'],
        ondelete='SET NULL',
    )
    op.create_foreign_key(
        'fk__property_property__owner_id',
        'property_property', 'user',
        ['owner_id'], ['id'],
        ondelete='SET NULL',
    )

    # Convertir build_year de Text à Integer
    op.alter_column(
        'property_property',
        'build_year',
        existing_type=sa.Text(),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using='build_year::integer',
    )


def downgrade() -> None:
    op.alter_column(
        'property_property',
        'build_year',
        existing_type=sa.Integer(),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.drop_constraint(
        'fk__property_property__owner_id', 'property_property', type_='foreignkey'
    )
    op.drop_constraint(
        'fk__property_property__building_id', 'property_property', type_='foreignkey'
    )
