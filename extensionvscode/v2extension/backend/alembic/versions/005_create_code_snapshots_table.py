"""create code_snapshots table

Revision ID: 005
Revises: 004
Create Date: 2025-12-28 02:34:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create code_snapshots table."""
    op.create_table(
        'code_snapshots',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('task_id', sa.String(36), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('language', sa.String(50), nullable=False),
        sa.Column('code_content', sa.Text(), nullable=False),
        sa.Column('validation_passed', sa.Boolean(), nullable=True),
        sa.Column('validation_score', sa.Float(), nullable=True),
        sa.Column('validation_feedback', sa.Text(), nullable=True),
        sa.Column('issues_found', JSON, nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('storage_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create indexes
    op.create_index('idx_code_snapshots_task_id', 'code_snapshots', ['task_id', 'created_at'])
    op.create_index('idx_code_snapshots_user_id', 'code_snapshots', ['user_id'])
    op.create_index('idx_code_snapshots_language', 'code_snapshots', ['language', 'created_at'])
    op.create_index('idx_code_snapshots_validated', 'code_snapshots', ['validation_passed', 'created_at'])
    op.create_index('idx_code_snapshots_user_lang', 'code_snapshots', ['user_id', 'language', 'created_at'])


def downgrade() -> None:
    """Drop code_snapshots table."""
    op.drop_index('idx_code_snapshots_user_lang', 'code_snapshots')
    op.drop_index('idx_code_snapshots_validated', 'code_snapshots')
    op.drop_index('idx_code_snapshots_language', 'code_snapshots')
    op.drop_index('idx_code_snapshots_user_id', 'code_snapshots')
    op.drop_index('idx_code_snapshots_task_id', 'code_snapshots')
    op.drop_table('code_snapshots')
