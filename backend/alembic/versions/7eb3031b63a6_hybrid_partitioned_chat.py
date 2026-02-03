"""add hybrid partitioned chat messages

Revision ID: 7eb3031b63a6
Revises: fc11485a2053
Create Date: 2026-02-03 01:15:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7eb3031b63a6'
down_revision = 'fc11485a2053'
branch_labels = None
depends_on = None

def upgrade():
    # Enable required extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    
    # Create main partitioned table (range by date)
    op.execute("""
        CREATE TABLE public.chat_messages (
            id BIGSERIAL,
            session_id UUID NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb,
            
            PRIMARY KEY (id, created_at),
            CONSTRAINT fk_chat_messages_user FOREIGN KEY (user_id) 
                REFERENCES users(id) ON DELETE CASCADE
        ) PARTITION BY RANGE (created_at)
    """)
    
    # Create partitions for the next 7 days
    op.execute("""
        CREATE TABLE public.chat_messages_default
        PARTITION OF public.chat_messages
        DEFAULT
    """)    
    # Create indexes
    op.execute("""
        CREATE INDEX idx_chat_session_time 
        ON public.chat_messages (session_id, created_at DESC)
    """)
    
    op.execute("""
        CREATE INDEX idx_chat_user_time 
        ON public.chat_messages (user_id, created_at DESC)
    """)
    
    op.execute("""
        CREATE INDEX idx_chat_metadata 
        ON public.chat_messages USING GIN (metadata)
    """)


def downgrade() -> None:
    # Drop table (will cascade to all partitions)
    op.execute("DROP TABLE IF EXISTS public.chat_messages CASCADE")