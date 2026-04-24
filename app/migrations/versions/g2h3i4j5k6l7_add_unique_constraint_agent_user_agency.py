"""Add unique constraint on agent(user_id, agency_id)

Revision ID: g2h3i4j5k6l7
Revises: d1e2f3a4b5c6
Create Date: 2026-04-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'g2h3i4j5k6l7'
down_revision: Union[str, Sequence[str], None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("ux_agent_user_agency", "agent", ["user_id", "agency_id"])


def downgrade() -> None:
    op.drop_constraint("ux_agent_user_agency", "agent", type_="unique")
