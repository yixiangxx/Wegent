"""add published_contents table

Revision ID: 88eb750699b0
Revises: z6a7b8c9d0e1
Create Date: 2026-03-02 16:52:02.080315+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88eb750699b0'
down_revision: Union[str, Sequence[str], None] = 'z6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create published_contents table
    op.create_table(
        'published_contents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subtask_id', sa.Integer(), nullable=False),
        sa.Column('attachment_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subtask_id', 'attachment_id', name='uniq_subtask_attachment')
    )

    # Create indexes
    op.create_index('ix_published_contents_id', 'published_contents', ['id'])
    op.create_index('ix_published_contents_user_id', 'published_contents', ['user_id'])
    op.create_index('ix_published_contents_subtask_id', 'published_contents', ['subtask_id'])
    op.create_index('ix_published_contents_attachment_id', 'published_contents', ['attachment_id'])
    op.create_index('ix_published_contents_created_at', 'published_contents', ['created_at'])
    op.create_index('idx_published_content_type_active', 'published_contents', ['content_type', 'is_active'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_published_content_type_active', table_name='published_contents')
    op.drop_index('ix_published_contents_created_at', table_name='published_contents')
    op.drop_index('ix_published_contents_attachment_id', table_name='published_contents')
    op.drop_index('ix_published_contents_subtask_id', table_name='published_contents')
    op.drop_index('ix_published_contents_user_id', table_name='published_contents')
    op.drop_index('ix_published_contents_id', table_name='published_contents')

    # Drop table
    op.drop_table('published_contents')
