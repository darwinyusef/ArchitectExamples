"""create goals table

Revision ID: 003
Revises: 002
Create Date: 2025-12-28 02:32:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, ENUM


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create goals table."""
    # Create ENUM types if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE goalstatus AS ENUM ('pending', 'in_progress', 'completed', 'blocked', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE goalpriority AS ENUM ('low', 'medium', 'high', 'urgent');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    goal_status_enum = ENUM(
        'pending', 'in_progress', 'completed', 'blocked', 'cancelled',
        name='goalstatus',
        create_type=False
    )

    goal_priority_enum = ENUM(
        'low', 'medium', 'high', 'urgent',
        name='goalpriority',
        create_type=False
    )

    op.create_table(
        'goals',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('course_id', sa.String(36), sa.ForeignKey('courses.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', goal_status_enum, nullable=False, server_default='pending'),
        sa.Column('priority', goal_priority_enum, nullable=False, server_default='medium'),
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('validation_criteria', JSON, nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
    )

    # Create indexes
    op.create_index('idx_goals_user_id', 'goals', ['user_id'])
    op.create_index('idx_goals_course_id', 'goals', ['course_id'])
    op.create_index('idx_goals_status', 'goals', ['status', 'created_at'])
    op.create_index('idx_goals_priority', 'goals', ['priority', 'created_at'])


def downgrade() -> None:
    """Drop goals table."""
    op.drop_index('idx_goals_priority', 'goals')
    op.drop_index('idx_goals_status', 'goals')
    op.drop_index('idx_goals_course_id', 'goals')
    op.drop_index('idx_goals_user_id', 'goals')
    op.drop_table('goals')

    # Drop ENUM types
    goal_priority_enum = ENUM(name='goalpriority')
    goal_priority_enum.drop(op.get_bind())

    goal_status_enum = ENUM(name='goalstatus')
    goal_status_enum.drop(op.get_bind())
