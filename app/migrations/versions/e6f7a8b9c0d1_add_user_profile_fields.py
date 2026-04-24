"""Add bio and social media URL fields to user table

Revision ID: e6f7a8b9c0d1
Revises: c1d2e3f4a5b6
Create Date: 2026-04-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6f7a8b9c0d1'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('facebook_url', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('x_url', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('linkedin_url', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('instagram_url', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('youtube_url', sa.Text(), nullable=True))
    op.add_column('user', sa.Column('tiktok_url', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'tiktok_url')
    op.drop_column('user', 'youtube_url')
    op.drop_column('user', 'instagram_url')
    op.drop_column('user', 'linkedin_url')
    op.drop_column('user', 'x_url')
    op.drop_column('user', 'facebook_url')
    op.drop_column('user', 'bio')
