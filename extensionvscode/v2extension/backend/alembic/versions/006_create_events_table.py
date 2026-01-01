"""create events table

Revision ID: 006
Revises: 005
Create Date: 2025-12-28 02:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, ENUM


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create events table."""
    # Create ENUM type for event types if it doesn't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE eventtype AS ENUM (
                'user.created', 'user.updated', 'user.login', 'user.logout',
                'course.created', 'course.updated', 'course.completed', 'course.archived',
                'goal.created', 'goal.updated', 'goal.started', 'goal.completed', 'goal.blocked',
                'task.created', 'task.updated', 'task.started', 'task.completed',
                'task.validated', 'task.failed',
                'code.submitted', 'code.reviewed', 'code.validated',
                'ai.feedback.generated', 'ai.goal.suggested', 'ai.validation.completed',
                'system.error', 'system.warning'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    event_type_enum = ENUM(
        # User events
        'user.created', 'user.updated', 'user.login', 'user.logout',
        # Course events
        'course.created', 'course.updated', 'course.completed', 'course.archived',
        # Goal events
        'goal.created', 'goal.updated', 'goal.started', 'goal.completed', 'goal.blocked',
        # Task events
        'task.created', 'task.updated', 'task.started', 'task.completed',
        'task.validated', 'task.failed',
        # Code events
        'code.submitted', 'code.reviewed', 'code.validated',
        # AI events
        'ai.feedback.generated', 'ai.goal.suggested', 'ai.validation.completed',
        # System events
        'system.error', 'system.warning',
        name='eventtype',
        create_type=False
    )

    op.create_table(
        'events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type', event_type_enum, nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.String(36), nullable=True),
        sa.Column('payload', JSON, nullable=False),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('parquet_path', sa.String(500), nullable=True),
    )

    # Create indexes (compound indexes for common queries)
    op.create_index('idx_events_user_created', 'events', ['user_id', 'created_at'])
    op.create_index('idx_events_entity', 'events', ['entity_type', 'entity_id', 'created_at'])
    op.create_index('idx_events_type_created', 'events', ['event_type', 'created_at'])
    op.create_index('idx_events_created_at', 'events', ['created_at'])


def downgrade() -> None:
    """Drop events table."""
    op.drop_index('idx_events_created_at', 'events')
    op.drop_index('idx_events_type_created', 'events')
    op.drop_index('idx_events_entity', 'events')
    op.drop_index('idx_events_user_created', 'events')
    op.drop_table('events')

    # Drop ENUM type
    event_type_enum = ENUM(name='eventtype')
    event_type_enum.drop(op.get_bind())
