from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Enum, func
from sqlalchemy.types import TypeDecorator, VARCHAR
import enum
from database.config import Base
from datetime import datetime


class RecipientTypeEnum(str, enum.Enum):
    """Enum for notification recipient types"""
    USER = "USER"
    LAWYER = "LAWYER"
    ADMIN = "ADMIN"  # For future extensibility


class NotificationTypeEnum(str, enum.Enum):
    """Enum for notification categories"""
    SYSTEM = "SYSTEM"                    # System announcements, maintenance
    CASE_UPDATE = "CASE_UPDATE"          # Case status changes, new messages
    PAYMENT = "PAYMENT"                  # Payment confirmations, invoices
    VERIFICATION = "VERIFICATION"        # Lawyer verification updates
    DOCUMENT = "DOCUMENT"                # Document uploads, requests
    APPOINTMENT = "APPOINTMENT"          # Meeting scheduling, reminders
    MESSAGE = "MESSAGE"                  # Direct messages, chat notifications
    LEGAL_UPDATE = "LEGAL_UPDATE"        # Legal news, regulation changes
    PROFILE = "PROFILE"                  # Profile updates, requirements


class Notification(Base):
    """
    Unified notification model for all user types.
    
    Design Benefits:
    1. Single source of truth for all notifications
    2. Consistent notification behavior across user types
    3. Simplified queries and maintenance
    4. Easy to add new recipient types (Admin, Judge, Staff)
    5. Better data integrity and relationships
    6. Unified notification analytics and reporting
    """
    __tablename__ = "notifications"

    # Primary identifiers
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, nullable=False, index=True)  # References user/lawyer ID
    recipient_type = Column(Enum(RecipientTypeEnum), nullable=False, index=True)
    
    # Content fields
    title = Column(String(200), nullable=True)  # Optional short heading
    message = Column(Text, nullable=False)       # Main notification content
    type = Column(Enum(NotificationTypeEnum), nullable=False, default=NotificationTypeEnum.SYSTEM)
    
    # State management
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    read_at = Column(TIMESTAMP, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)  # Soft delete
    
    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now())
    
    # Optional metadata for extensibility
    metadata_json = Column(Text, nullable=True)  # JSON string for additional data
    action_url = Column(String(500), nullable=True)  # Deep link for actions
    priority = Column(Integer, nullable=False, default=1)  # 1=low, 2=medium, 3=high
    expires_at = Column(TIMESTAMP, nullable=True)  # For time-sensitive notifications
    
    # Composite indexes for performance
    __table_args__ = (
        # Most common query patterns
        {'mysql_engine': 'InnoDB'},
    )
    
    def __repr__(self):
        return f"<Notification(id={self.id}, recipient={self.recipient_type}:{self.recipient_id}, type={self.type})>"
    
    def mark_as_read(self) -> None:
        """Mark notification as read with timestamp"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def soft_delete(self) -> None:
        """Soft delete the notification"""
        self.is_deleted = True
    
    @property
    def is_urgent(self) -> bool:
        """Check if notification is high priority"""
        return self.priority >= 3
    
    @property
    def is_expired(self) -> bool:
        """Check if notification has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


