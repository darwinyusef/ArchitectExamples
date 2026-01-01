"""create courses table

Revision ID: 002
Revises: 001
Create Date: 2025-12-28 02:31:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, ENUM


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create courses table."""
    # Create ENUM type if it doesn't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE coursestatus AS ENUM ('draft', 'active', 'completed', 'archived');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    course_status_enum = ENUM(
        'draft', 'active', 'completed', 'archived',
        name='coursestatus',
        create_type=False
    )

    op.create_table(
        'courses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', course_status_enum, nullable=False, server_default='draft'),
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # Create indexes
    op.create_index('idx_courses_user_id', 'courses', ['user_id'])
    op.create_index('idx_courses_status', 'courses', ['status', 'created_at'])


def downgrade() -> None:
    """Drop courses table."""
    op.drop_index('idx_courses_status', 'courses')
    op.drop_index('idx_courses_user_id', 'courses')
    op.drop_table('courses')

    # Drop ENUM type
    course_status_enum = ENUM(name='coursestatus')
    course_status_enum.drop(op.get_bind())
