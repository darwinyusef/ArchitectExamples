"""create tasks table

Revision ID: 004
Revises: 003
Create Date: 2025-12-28 02:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, ENUM


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tasks table."""
    # Create ENUM types if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE taskstatus AS ENUM ('todo', 'in_progress', 'in_review', 'completed', 'failed', 'skipped');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tasktype AS ENUM ('code', 'documentation', 'testing', 'research', 'review', 'deployment', 'other');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    task_status_enum = ENUM(
        'todo', 'in_progress', 'in_review', 'completed', 'failed', 'skipped',
        name='taskstatus',
        create_type=False
    )

    task_type_enum = ENUM(
        'code', 'documentation', 'testing', 'research', 'review', 'deployment', 'other',
        name='tasktype',
        create_type=False
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('goal_id', sa.String(36), sa.ForeignKey('goals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', task_type_enum, nullable=False, server_default='code'),
        sa.Column('status', task_status_enum, nullable=False, server_default='todo'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('actual_hours', sa.Float(), nullable=True),
        sa.Column('validation_result', JSON, nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # Create indexes
    op.create_index('idx_tasks_goal_id', 'tasks', ['goal_id'])
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status', 'created_at'])
    op.create_index('idx_tasks_type', 'tasks', ['task_type', 'created_at'])


def downgrade() -> None:
    """Drop tasks table."""
    op.drop_index('idx_tasks_type', 'tasks')
    op.drop_index('idx_tasks_status', 'tasks')
    op.drop_index('idx_tasks_user_id', 'tasks')
    op.drop_index('idx_tasks_goal_id', 'tasks')
    op.drop_table('tasks')

    # Drop ENUM types
    task_type_enum = ENUM(name='tasktype')
    task_type_enum.drop(op.get_bind())

    task_status_enum = ENUM(name='taskstatus')
    task_status_enum.drop(op.get_bind())
