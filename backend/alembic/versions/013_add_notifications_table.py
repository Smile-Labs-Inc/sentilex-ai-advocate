"""add notifications table

Revision ID: 013_add_notifications_table
Revises: 012_s3_evidence_refactor
Create Date: 2026-02-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '013_add_notifications_table'
down_revision = '012_s3_evidence_refactor'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notifications table (ENUMs will be created automatically by SQLAlchemy)
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('recipient_type', postgresql.ENUM('USER', 'LAWYER', 'ADMIN', name='recipient_type'), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', postgresql.ENUM(
            'SYSTEM', 'CASE_UPDATE', 'PAYMENT', 'VERIFICATION', 'DOCUMENT', 
            'APPOINTMENT', 'MESSAGE', 'LEGAL_UPDATE', 'PROFILE', 
            name='notification_type'
        ), nullable=False, server_default='SYSTEM'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes for performance optimization
    op.create_index('ix_notifications_recipient', 'notifications', ['recipient_id', 'recipient_type'])
    op.create_index('ix_notifications_unread', 'notifications', ['recipient_id', 'recipient_type', 'is_read', 'is_deleted'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])
    op.create_index('ix_notifications_priority', 'notifications', ['priority'])
    op.create_index('ix_notifications_expires', 'notifications', ['expires_at'])
    
    # Composite indexes for common query patterns
    op.create_index('ix_notifications_recipient_unread_created', 'notifications', 
                    ['recipient_id', 'recipient_type', 'is_read', 'created_at'])
    op.create_index('ix_notifications_recipient_type_created', 'notifications', 
                    ['recipient_id', 'recipient_type', 'type', 'created_at'])
    
    # Add updated_at trigger for PostgreSQL
    op.execute("""
        CREATE OR REPLACE FUNCTION update_notifications_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER update_notifications_updated_at
        BEFORE UPDATE ON notifications
        FOR EACH ROW
        EXECUTE FUNCTION update_notifications_updated_at();
    """)


def downgrade() -> None:
    # Drop the trigger and function
    op.execute("DROP TRIGGER IF EXISTS update_notifications_updated_at ON notifications;")
    op.execute("DROP FUNCTION IF EXISTS update_notifications_updated_at();")
    
    # Drop indexes
    op.drop_index('ix_notifications_recipient_type_created', table_name='notifications')
    op.drop_index('ix_notifications_recipient_unread_created', table_name='notifications')
    op.drop_index('ix_notifications_expires', table_name='notifications')
    op.drop_index('ix_notifications_priority', table_name='notifications')
    op.drop_index('ix_notifications_type', table_name='notifications')
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_unread', table_name='notifications')
    op.drop_index('ix_notifications_recipient', table_name='notifications')
    
    # Drop the table (ENUMs will be dropped automatically by SQLAlchemy)
    op.drop_table('notifications')