"""Add chat messages and evidence tables

Revision ID: 006_add_chat_messages_and_evidence_tables
Revises: 005_add_profile_completed_fields
Create Date: 2026-02-02 23:18:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_chat_evidence'
down_revision = '005a_add_incidents_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create incident_chat_messages table
    op.create_table(
        'incident_chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ASSISTANT', 'SYSTEM', name='incident_msg_role_type'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incident_chat_messages_id'), 'incident_chat_messages', ['id'], unique=False)
    op.create_index(op.f('ix_incident_chat_messages_incident_id'), 'incident_chat_messages', ['incident_id'], unique=False)

    # Create evidence table
    op.create_table(
        'evidence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evidence_id'), 'evidence', ['id'], unique=False)
    op.create_index(op.f('ix_evidence_incident_id'), 'evidence', ['incident_id'], unique=False)


def downgrade() -> None:
    # Drop evidence table
    op.drop_index(op.f('ix_evidence_incident_id'), table_name='evidence')
    op.drop_index(op.f('ix_evidence_id'), table_name='evidence')
    op.drop_table('evidence')

    # Drop incident_chat_messages table
    op.drop_index(op.f('ix_incident_chat_messages_incident_id'), table_name='incident_chat_messages')
    op.drop_index(op.f('ix_incident_chat_messages_id'), table_name='incident_chat_messages')
    op.drop_table('incident_chat_messages')

