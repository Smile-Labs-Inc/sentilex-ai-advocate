"""Add lawyer verification system

Revision ID: 001_add_verification
Revises: 
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001_add_verification'
down_revision = '000_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    verification_status_enum = sa.Enum('not_started', 'in_progress', 'submitted', 'approved', 'rejected', 
                                       name='verificationstatusenum')
    
    # Explicitly create the ENUM type in the database
    verification_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Add verification columns to lawyers table
    op.add_column('lawyers', sa.Column('verification_step', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('lawyers', sa.Column('verification_status', 
                                       verification_status_enum,
                                       nullable=False, server_default='not_started'))
    op.add_column('lawyers', sa.Column('verification_submitted_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('lawyers', sa.Column('verification_updated_at', sa.TIMESTAMP(), nullable=True))
    
    # Step 2: Legal enrollment details columns
    op.add_column('lawyers', sa.Column('sc_enrollment_number', sa.String(50), nullable=True))
    op.add_column('lawyers', sa.Column('enrollment_year', sa.Integer(), nullable=True))
    op.add_column('lawyers', sa.Column('law_college_reg_number', sa.String(50), nullable=True))
    
    # Step 3: Document storage columns (URLs + metadata only)
    # NIC Front
    op.add_column('lawyers', sa.Column('nic_front_url', sa.String(500), nullable=True))
    op.add_column('lawyers', sa.Column('nic_front_hash', sa.String(64), nullable=True))
    op.add_column('lawyers', sa.Column('nic_front_uploaded_at', sa.TIMESTAMP(), nullable=True))
    
    # NIC Back
    op.add_column('lawyers', sa.Column('nic_back_url', sa.String(500), nullable=True))
    op.add_column('lawyers', sa.Column('nic_back_hash', sa.String(64), nullable=True))
    op.add_column('lawyers', sa.Column('nic_back_uploaded_at', sa.TIMESTAMP(), nullable=True))
    
    # Attorney Certificate
    op.add_column('lawyers', sa.Column('attorney_certificate_url', sa.String(500), nullable=True))
    op.add_column('lawyers', sa.Column('attorney_certificate_hash', sa.String(64), nullable=True))
    op.add_column('lawyers', sa.Column('attorney_certificate_uploaded_at', sa.TIMESTAMP(), nullable=True))
    
    # Practising Certificate
    op.add_column('lawyers', sa.Column('practising_certificate_url', sa.String(500), nullable=True))
    op.add_column('lawyers', sa.Column('practising_certificate_hash', sa.String(64), nullable=True))
    op.add_column('lawyers', sa.Column('practising_certificate_uploaded_at', sa.TIMESTAMP(), nullable=True))
    
    # Step 4: Declaration columns
    op.add_column('lawyers', sa.Column('declaration_accepted', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('lawyers', sa.Column('declaration_accepted_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('lawyers', sa.Column('declaration_ip_address', sa.String(45), nullable=True))
    
    # Admin verification columns
    op.add_column('lawyers', sa.Column('verified_by_admin_id', sa.Integer(), nullable=True))
    op.add_column('lawyers', sa.Column('verified_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('lawyers', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.add_column('lawyers', sa.Column('admin_notes', sa.Text(), nullable=True))
    
    # Create indexes for performance
    op.create_index('idx_sc_enrollment', 'lawyers', ['sc_enrollment_number'], unique=True)
    op.create_index('idx_verification_status', 'lawyers', ['verification_status'])
    
    # Create audit log table
    op.create_table(
        'lawyer_verification_audit',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('lawyer_id', sa.Integer(), sa.ForeignKey('lawyers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=True),
        sa.Column('performed_by', sa.String(50), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False)
    )
    
    # Create indexes on audit table
    op.create_index('idx_audit_lawyer', 'lawyer_verification_audit', ['lawyer_id'])
    op.create_index('idx_audit_created', 'lawyer_verification_audit', ['created_at'])
    op.create_index('idx_audit_action', 'lawyer_verification_audit', ['action'])


def downgrade() -> None:
    # Drop audit table
    op.drop_index('idx_audit_action', 'lawyer_verification_audit')
    op.drop_index('idx_audit_created', 'lawyer_verification_audit')
    op.drop_index('idx_audit_lawyer', 'lawyer_verification_audit')
    op.drop_table('lawyer_verification_audit')
    
    # Drop indexes from lawyers table
    op.drop_index('idx_verification_status', 'lawyers')
    op.drop_index('idx_sc_enrollment', 'lawyers')
    
    # Drop all added columns from lawyers table
    columns_to_drop = [
        'verification_step', 'verification_status', 'verification_submitted_at', 'verification_updated_at',
        'sc_enrollment_number', 'enrollment_year', 'law_college_reg_number',
        'nic_front_url', 'nic_front_hash', 'nic_front_uploaded_at',
        'nic_back_url', 'nic_back_hash', 'nic_back_uploaded_at',
        'attorney_certificate_url', 'attorney_certificate_hash', 'attorney_certificate_uploaded_at',
        'practising_certificate_url', 'practising_certificate_hash', 'practising_certificate_uploaded_at',
        'declaration_accepted', 'declaration_accepted_at', 'declaration_ip_address',
        'verified_by_admin_id', 'verified_at', 'rejection_reason', 'admin_notes'
    ]
    
    for column in columns_to_drop:
        op.drop_column('lawyers', column)
    
    # Drop the ENUM type
    sa.Enum(name='verificationstatusenum').drop(op.get_bind(), checkfirst=True)
