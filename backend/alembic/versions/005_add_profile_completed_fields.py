"""add_profile_completed_fields

Revision ID: fc11485a2053
Revises: cb7f6be58644
Create Date: 2026-01-31 11:13:47.460568

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError, ProgrammingError


# revision identifiers, used by Alembic.
revision = '005_add_profile_completed_fields'
down_revision = '004_add_oauth_to_lawyers'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check and add profile_completed column to users table
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if users table exists before trying to modify it
    existing_tables = inspector.get_table_names()
    
    if 'users' in existing_tables:
        users_columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'profile_completed' not in users_columns:
            op.add_column('users', sa.Column('profile_completed', sa.Boolean(), nullable=False, server_default='0'))
        
        # Make some fields nullable for OAuth users (only if needed)
        try:
            op.alter_column('users', 'district', nullable=True)
        except (OperationalError, ProgrammingError):
            pass  # Already nullable or column doesn't exist
    
    # Check and add profile_completed column to lawyers table
    if 'lawyers' in existing_tables:
        lawyers_columns = [col['name'] for col in inspector.get_columns('lawyers')]
        
        if 'profile_completed' not in lawyers_columns:
            op.add_column('lawyers', sa.Column('profile_completed', sa.Boolean(), nullable=False, server_default='0'))
        
        # Make some fields nullable for OAuth users (only if needed)
        try:
            op.alter_column('lawyers', 'phone', nullable=True)
            op.alter_column('lawyers', 'specialties', nullable=True)
            op.alter_column('lawyers', 'experience_years', nullable=True)
            op.alter_column('lawyers', 'district', nullable=True)
        except (OperationalError, ProgrammingError):
            pass  # Already nullable or column doesn't exist


def downgrade() -> None:
    # Revert nullable changes (only if tables exist)
    try:
        op.alter_column('lawyers', 'district', nullable=False)
        op.alter_column('lawyers', 'experience_years', nullable=False)
        op.alter_column('lawyers', 'specialties', nullable=False)
        op.alter_column('lawyers', 'phone', nullable=False)
    except (OperationalError, ProgrammingError):
        pass  # Table doesn't exist or columns don't exist
    
    try:
        op.alter_column('users', 'district', nullable=False)
    except (OperationalError, ProgrammingError):
        pass  # Table doesn't exist or column doesn't exist
    
    # Remove profile_completed columns (only if tables exist)
    try:
        op.drop_column('lawyers', 'profile_completed')
    except (OperationalError, ProgrammingError):
        pass  # Table doesn't exist or column doesn't exist
    
    try:
        op.drop_column('users', 'profile_completed')
    except (OperationalError, ProgrammingError):
        pass  # Table doesn't exist or column doesn't exist
