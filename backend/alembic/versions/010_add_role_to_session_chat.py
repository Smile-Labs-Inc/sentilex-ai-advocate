"""add role column to session chat messages

Revision ID: 010_add_role_to_session_chat
Revises: 009_add_chat_sessions
Create Date: 2026-02-03 10:13:34.223503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_add_role_to_session_chat'
down_revision = '009_add_chat_sessions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column to session_chat_messages table
    op.execute("""
        ALTER TABLE public.session_chat_messages 
        ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user'
    """)


def downgrade() -> None:
    # Remove role column from session_chat_messages table
    op.execute("""
        ALTER TABLE public.session_chat_messages 
        DROP COLUMN IF EXISTS role
    """)
