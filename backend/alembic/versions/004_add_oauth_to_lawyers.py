"""add_oauth_to_lawyers

Revision ID: cb7f6be58644
Revises: 003_add_mfa_password
Create Date: 2026-01-31 11:00:34.417676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_oauth_to_lawyers'
down_revision = '003_add_mfa_password'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add OAuth columns to lawyers table
    op.add_column('lawyers', sa.Column('oauth_provider', sa.String(20), nullable=True))
    op.add_column('lawyers', sa.Column('oauth_id', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove OAuth columns from lawyers table
    op.drop_column('lawyers', 'oauth_id')
    op.drop_column('lawyers', 'oauth_provider')
