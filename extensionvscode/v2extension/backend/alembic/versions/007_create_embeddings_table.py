"""create embeddings table with pgvector

Revision ID: 007
Revises: 006
Create Date: 2025-12-28 02:36:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create embeddings table with pgvector extension."""
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table(
        'embeddings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(36), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),  # OpenAI text-embedding-3-small
        sa.Column('model', sa.String(100), nullable=False, server_default='text-embedding-3-small'),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create regular indexes
    op.create_index('idx_embeddings_user_id', 'embeddings', ['user_id'])
    op.create_index('idx_embeddings_entity', 'embeddings', ['entity_type', 'entity_id'])
    op.create_index('idx_embeddings_created_at', 'embeddings', ['created_at'])

    # Create HNSW index for vector similarity search
    # This is the most important index for RAG performance
    op.execute("""
        CREATE INDEX idx_embeddings_vector_hnsw
        ON embeddings
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    # Alternatively, create IVFFlat index (faster build, slower search):
    # op.execute("""
    #     CREATE INDEX idx_embeddings_vector_ivfflat
    #     ON embeddings
    #     USING ivfflat (embedding vector_cosine_ops)
    #     WITH (lists = 100)
    # """)


def downgrade() -> None:
    """Drop embeddings table and pgvector extension."""
    op.drop_index('idx_embeddings_vector_hnsw', 'embeddings')
    op.drop_index('idx_embeddings_created_at', 'embeddings')
    op.drop_index('idx_embeddings_entity', 'embeddings')
    op.drop_index('idx_embeddings_user_id', 'embeddings')
    op.drop_table('embeddings')

    # Note: We don't drop the extension as it might be used elsewhere
    # If you want to drop it: op.execute('DROP EXTENSION IF EXISTS vector')
