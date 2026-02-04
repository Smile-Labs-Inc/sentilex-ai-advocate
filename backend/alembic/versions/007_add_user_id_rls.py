"""Add user_id to chat_messages and setup RLS for agent access

Revision ID: 007_add_user_id_rls
Revises: 006_chat_evidence
Create Date: 2026-02-04 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_add_user_id_rls'
down_revision = '006_chat_evidence'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user_id column to incident_chat_messages
    op.add_column(
        'incident_chat_messages',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True)
    )
    op.create_index('ix_incident_chat_messages_user_id', 'incident_chat_messages', ['user_id'], unique=False)

    # Create agent_user role with read-only access
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'agent_user') THEN
                CREATE ROLE agent_user WITH LOGIN PASSWORD 'secure_agent_pass' NOSUPERUSER;
            END IF;
        END
        $$;
    """)

    # Grant SELECT permissions to agent_user
    op.execute("GRANT SELECT ON users, incidents, incident_chat_messages TO agent_user;")

    # Enable Row Level Security
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE incident_chat_messages ENABLE ROW LEVEL SECURITY;")

    # Create RLS policies for agent_user
    op.execute("""
        CREATE POLICY agent_user_policy ON users 
        FOR SELECT TO agent_user
        USING (id = current_setting('app.current_user_id', true)::integer);
    """)

    op.execute("""
        CREATE POLICY agent_incident_policy ON incidents 
        FOR SELECT TO agent_user
        USING (user_id = current_setting('app.current_user_id', true)::integer);
    """)

    op.execute("""
        CREATE POLICY agent_incident_chat_policy ON incident_chat_messages 
        FOR SELECT TO agent_user
        USING (user_id = current_setting('app.current_user_id', true)::integer);
    """)


def downgrade() -> None:
    # Drop RLS policies
    op.execute("DROP POLICY IF EXISTS agent_incident_chat_policy ON incident_chat_messages;")
    op.execute("DROP POLICY IF EXISTS agent_incident_policy ON incidents;")
    op.execute("DROP POLICY IF EXISTS agent_user_policy ON users;")

    # Disable RLS
    op.execute("ALTER TABLE incident_chat_messages DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE incidents DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")

    # Revoke permissions and drop role
    op.execute("REVOKE SELECT ON users, incidents, incident_chat_messages FROM agent_user;")
    op.execute("DROP ROLE IF EXISTS agent_user;")

    # Drop index and column
    op.drop_index('ix_incident_chat_messages_user_id', table_name='incident_chat_messages')
    op.drop_column('incident_chat_messages', 'user_id')
