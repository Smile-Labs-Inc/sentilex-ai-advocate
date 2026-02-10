#!/usr/bin/env python
"""
Script to create test notifications for the currently authenticated user.
This is useful for testing the notification system in development.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import SessionLocal
from models.notification import Notification, RecipientTypeEnum, NotificationTypeEnum
from models.user import User

def create_test_notifications():
    """Create test notifications for the first user in the database."""
    db = SessionLocal()
    
    try:
        # Get the first user
        user = db.query(User).first()
        if not user:
            print("No users found in the database. Please create a user first.")
            return
        
        print(f"Creating test notifications for user: {user.email}")
        
        # Create sample notifications
        notifications = [
            Notification(
                recipient_id=user.id,
                recipient_type=RecipientTypeEnum.USER,
                title="Welcome to SentiLex",
                message="Welcome! Your account is now active and ready to use.",
                notification_type=NotificationTypeEnum.SYSTEM_UPDATE,
                priority=1,
                created_at=datetime.utcnow(),
            ),
            Notification(
                recipient_id=user.id,
                recipient_type=RecipientTypeEnum.USER,
                title="New Incident Created",
                message="Your incident report has been received and is under review.",
                notification_type=NotificationTypeEnum.CASE_UPDATE,
                priority=2,
                created_at=datetime.utcnow() - timedelta(hours=2),
            ),
            Notification(
                recipient_id=user.id,
                recipient_type=RecipientTypeEnum.USER,
                title="Lawyer Available",
                message="A legal professional is available to consult with you.",
                notification_type=NotificationTypeEnum.LEGAL_CONSULTATION,
                priority=2,
                created_at=datetime.utcnow() - timedelta(hours=5),
            ),
            Notification(
                recipient_id=user.id,
                recipient_type=RecipientTypeEnum.USER,
                title="Document Uploaded",
                message="Your evidence document has been successfully processed.",
                notification_type=NotificationTypeEnum.CASE_UPDATE,
                priority=1,
                created_at=datetime.utcnow() - timedelta(days=1),
                read_at=datetime.utcnow() - timedelta(hours=12),  # This one is read
            ),
        ]
        
        db.add_all(notifications)
        db.commit()
        
        print(f"Successfully created {len(notifications)} test notifications!")
        print(f"\nNotifications created:")
        for notif in notifications:
            status = "read" if notif.read_at else "unread"
            print(f"  - {notif.title} ({status})")
        
    except Exception as e:
        print(f"Error creating test notifications: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_notifications()
