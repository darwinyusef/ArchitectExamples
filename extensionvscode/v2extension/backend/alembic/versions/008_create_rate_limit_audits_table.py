"""create rate_limit_audits table

Revision ID: 008
Revises: 007
Create Date: 2025-12-28 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create rate_limit_audits table."""

    # Create enum types if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE ratelimitaction AS ENUM (
                'api_call',
                'embedding_generation',
                'chat_completion',
                'code_validation',
                'rag_search',
                'similarity_search',
                'bulk_create',
                'bulk_update'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE ratelimitstatus AS ENUM (
                'allowed',
                'rate_limited',
                'token_limit_exceeded',
                'quota_exceeded'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Define enum references (with create_type=False)
    rate_limit_action_enum = postgresql.ENUM(
        'api_call',
        'embedding_generation',
        'chat_completion',
        'code_validation',
        'rag_search',
        'similarity_search',
        'bulk_create',
        'bulk_update',
        name='ratelimitaction',
        create_type=False
    )

    rate_limit_status_enum = postgresql.ENUM(
        'allowed',
        'rate_limited',
        'token_limit_exceeded',
        'quota_exceeded',
        name='ratelimitstatus',
        create_type=False
    )

    # Create table
    op.create_table(
        'rate_limit_audits',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),

        # Request info
        sa.Column('endpoint', sa.String(200), nullable=False),
        sa.Column('method', sa.String(10), nullable=False),
        sa.Column('action', rate_limit_action_enum, nullable=False, index=True),

        # Rate limit status
        sa.Column('status', rate_limit_status_enum, nullable=False, index=True),
        sa.Column('allowed', sa.Boolean, default=True, nullable=False),

        # Token Bucket info
        sa.Column('tokens_requested', sa.Integer, default=1, nullable=False),
        sa.Column('tokens_available', sa.Integer, nullable=False),
        sa.Column('tokens_consumed', sa.Integer, default=0, nullable=False),

        # OpenAI token tracking
        sa.Column('openai_prompt_tokens', sa.Integer, nullable=True),
        sa.Column('openai_completion_tokens', sa.Integer, nullable=True),
        sa.Column('openai_total_tokens', sa.Integer, nullable=True),
        sa.Column('openai_model', sa.String(100), nullable=True),

        # Cost tracking
        sa.Column('estimated_cost_cents', sa.Float, nullable=True),

        # Response info
        sa.Column('response_time_ms', sa.Float, nullable=True),
        sa.Column('http_status_code', sa.Integer, nullable=True),

        # Rate limit details
        sa.Column('rate_limit_key', sa.String(200), nullable=False),
        sa.Column('rate_limit_window_seconds', sa.Integer, nullable=False),
        sa.Column('rate_limit_max_requests', sa.Integer, nullable=False),
        sa.Column('current_request_count', sa.Integer, nullable=False),

        # Alert flags
        sa.Column('is_suspicious', sa.Boolean, default=False, nullable=False),
        sa.Column('alert_triggered', sa.Boolean, default=False, nullable=False),
        sa.Column('alert_reason', sa.String(500), nullable=True),

        # IP and user agent
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),

        # Metadata
        sa.Column('metadata', postgresql.JSONB, default={}, nullable=False),

        # Timestamps
        sa.Column('timestamp', sa.DateTime, default=sa.func.now(), nullable=False, index=True),
    )

    # Create indexes for common queries
    op.create_index(
        'idx_rate_limit_audits_user_timestamp',
        'rate_limit_audits',
        ['user_id', 'timestamp']
    )

    op.create_index(
        'idx_rate_limit_audits_action_timestamp',
        'rate_limit_audits',
        ['action', 'timestamp']
    )

    op.create_index(
        'idx_rate_limit_audits_status_timestamp',
        'rate_limit_audits',
        ['status', 'timestamp']
    )

    op.create_index(
        'idx_rate_limit_audits_alert',
        'rate_limit_audits',
        ['alert_triggered', 'timestamp']
    )

    # Index for finding rate limits by user and action
    op.create_index(
        'idx_rate_limit_audits_user_action',
        'rate_limit_audits',
        ['user_id', 'action', 'timestamp']
    )


def downgrade() -> None:
    """Drop rate_limit_audits table."""

    op.drop_index('idx_rate_limit_audits_user_action')
    op.drop_index('idx_rate_limit_audits_alert')
    op.drop_index('idx_rate_limit_audits_status_timestamp')
    op.drop_index('idx_rate_limit_audits_action_timestamp')
    op.drop_index('idx_rate_limit_audits_user_timestamp')

    op.drop_table('rate_limit_audits')

    op.execute('DROP TYPE ratelimitstatus')
    op.execute('DROP TYPE ratelimitaction')
