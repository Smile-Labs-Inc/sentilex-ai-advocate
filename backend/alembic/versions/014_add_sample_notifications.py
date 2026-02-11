"""add sample notifications data

Revision ID: 014_add_sample_notifications
Revises: 013_add_notifications_table
Create Date: 2026-02-10 12:01:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '014_add_sample_notifications'
down_revision = '013_add_notifications_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add sample notifications for testing
    # Only run this if you want sample data in your database
    op.execute("""
        INSERT INTO notifications (
            recipient_id, recipient_type, title, message, type, priority, action_url
        ) VALUES 
        (1, 'LAWYER', Welcome to SentiLex', 
         'Welcome to the SentiLex AI Advocate platform! Please complete your profile verification to start accepting cases.', 
         'SYSTEM', 2, '/profile/verification'),
        
        (1, 'LAWYER', 'Verification Required', 
         'Please upload your legal license documents and Supreme Court enrollment certificate to complete verification.', 
         'VERIFICATION', 3, '/profile/verification'),
        
        (2, 'USER', ' Case Update', 
         'Your legal case status has been updated to "Under Review". Your assigned lawyer will contact you within 24 hours.', 
         'CASE_UPDATE', 2, '/cases/1'),
        
        (1, 'LAWYER', ' New Case Assignment', 
         'You have been assigned a new Personal Injury case. Please review the case details and respond to the client promptly.', 
         'CASE_UPDATE', 3, '/lawyer/cases/1'),
        
        (2, 'USER', ' Payment Confirmation', 
         'Your payment of $500 for legal consultation has been successfully processed. Receipt has been sent to your email.', 
         'PAYMENT', 1, '/payments/receipt/1');
    """)


def downgrade() -> None:
    # Remove sample notifications
    op.execute("""
        DELETE FROM notifications WHERE 
        title IN ('Welcome to SentiLex', 'Verification Required', 'Case Update', 
                 'New Case Assignment', 'Payment Confirmation');
    """)