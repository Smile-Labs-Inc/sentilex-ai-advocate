"""add chat sessions table

Revision ID: a3f9c2e5d8b1
Revises: 7eb3031b63a6
Create Date: 2026-02-03 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a3f9c2e5d8b1'
down_revision = '7eb3031b63a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('last_message', sa.Text()),
        sa.Column('message_count', sa.BigInteger(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Create indexes
    op.create_index('ix_chat_sessions_user_updated', 'chat_sessions', ['user_id', 'updated_at'])


def downgrade() -> None:
    op.drop_index('ix_chat_sessions_user_updated', table_name='chat_sessions')
    op.drop_table('chat_sessions')
