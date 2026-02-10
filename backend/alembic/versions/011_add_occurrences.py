"""add occurrences table

Revision ID: 011_add_occurrences
Revises: 010_add_role_to_session_chat
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011_add_occurrences'
down_revision = '010_add_role_to_session_chat'
branch_labels = None
depends_on = None


def upgrade():
    # Get database connection
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    # Create occurrences table if it doesn't exist
    if 'occurrences' not in tables:
        op.create_table(
            'occurrences',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('incident_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('date_occurred', sa.Date(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_occurrences_id', 'occurrences', ['id'])
        op.create_index('ix_occurrences_incident_id', 'occurrences', ['incident_id'])
        op.create_index('ix_occurrences_date_occurred', 'occurrences', ['date_occurred'])
    
    # Check if occurrence_id column exists in evidence table
    columns = [col['name'] for col in inspector.get_columns('evidence')]
    
    if 'occurrence_id' not in columns:
        # Add occurrence_id to evidence table
        op.add_column('evidence', sa.Column('occurrence_id', sa.Integer(), nullable=True))
        op.create_index('ix_evidence_occurrence_id', 'evidence', ['occurrence_id'])
        op.create_foreign_key(
            'fk_evidence_occurrence_id', 
            'evidence', 'occurrences',
            ['occurrence_id'], ['id'],
            ondelete='SET NULL'
        )


def downgrade():
    # Remove occurrence_id from evidence table
    op.drop_constraint('fk_evidence_occurrence_id', 'evidence', type_='foreignkey')
    op.drop_index('ix_evidence_occurrence_id', 'evidence')
    op.drop_column('evidence', 'occurrence_id')
    
    # Drop occurrences table
    op.drop_index('ix_occurrences_date_occurred', 'occurrences')
    op.drop_index('ix_occurrences_incident_id', 'occurrences')
    op.drop_index('ix_occurrences_id', 'occurrences')
    op.drop_table('occurrences')
