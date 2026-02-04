"""add_role_column_to_chat_messages

Revision ID: 76bcd6658bef
Revises: a3f9c2e5d8b1
Create Date: 2026-02-03 10:13:34.223503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76bcd6658bef'
down_revision = 'a3f9c2e5d8b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column to chat_messages table
    op.execute("""
        ALTER TABLE public.chat_messages 
        ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user'
    """)


def downgrade() -> None:
    # Remove role column from chat_messages table
    op.execute("""
        ALTER TABLE public.chat_messages 
        DROP COLUMN IF EXISTS role
    """)
