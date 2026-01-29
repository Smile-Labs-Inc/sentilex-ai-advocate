"""Initial database schema

Revision ID: 000_initial
Revises: 
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '000_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial lawyers table"""
    
    # Create lawyers table with basic fields
    op.create_table(
        'lawyers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('specialties', sa.String(255), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('district', sa.String(50), nullable=False),
        sa.Column('availability', sa.String(50), server_default='Available'),
        sa.Column('rating', sa.Numeric(2, 1), server_default='0.0'),
        sa.Column('reviews_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
    )
    
    # Create unique constraint and index on email
    op.create_unique_constraint('uq_lawyer_email', 'lawyers', ['email'])
    op.create_index('idx_lawyer_email', 'lawyers', ['email'])


def downgrade() -> None:
    """Drop lawyers table"""
    op.drop_index('idx_lawyer_email', 'lawyers')
    op.drop_constraint('uq_lawyer_email', 'lawyers', type_='unique')
    op.drop_table('lawyers')
