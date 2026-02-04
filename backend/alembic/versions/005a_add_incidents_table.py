"""Add incidents table

Revision ID: 005a_add_incidents_table
Revises: 005_add_profile_completed_fields
Create Date: 2026-02-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005a_add_incidents_table'
down_revision = '005_add_profile_completed_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create incident status enum (only if it doesn't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE incidentstatusenum AS ENUM ('draft', 'submitted', 'under_review', 'resolved');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create incident type enum (only if it doesn't exist)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE incidenttypeenum AS ENUM ('cyberbullying', 'harassment', 'stalking', 'non-consensual-leak', 'identity-theft', 'online-fraud', 'other');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create incidents table
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('incident_type', postgresql.ENUM('cyberbullying', 'harassment', 'stalking', 'non-consensual-leak', 'identity-theft', 'online-fraud', 'other', name='incidenttypeenum', create_type=False), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('date_occurred', sa.Date(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('jurisdiction', sa.String(length=100), nullable=True),
        sa.Column('platforms_involved', sa.String(length=500), nullable=True),
        sa.Column('perpetrator_info', sa.Text(), nullable=True),
        sa.Column('evidence_notes', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('draft', 'submitted', 'under_review', 'resolved', name='incidentstatusenum', create_type=False), nullable=False, server_default='submitted'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incidents_id'), 'incidents', ['id'], unique=False)
    op.create_index(op.f('ix_incidents_user_id'), 'incidents', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_incidents_user_id'), table_name='incidents')
    op.drop_index(op.f('ix_incidents_id'), table_name='incidents')
    op.drop_table('incidents')
    
    # Note: We don't drop the enums here as they may be used by other tables
    # If needed, manually drop with: DROP TYPE IF EXISTS incidentstatusenum, incidenttypeenum;
