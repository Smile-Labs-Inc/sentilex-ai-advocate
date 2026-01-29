"""
Active Session Tracking Model

Tracks active user sessions for security and session management.
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, Text, Index
from sqlalchemy.sql import func
from database.config import Base


class ActiveSession(Base):
    """
    Track active user sessions for security and management.
    
    Features:
    - View all active sessions
    - Remote logout capability
    - Device/browser identification
    - Session expiration tracking
    """
    __tablename__ = "active_sessions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Token Identification
    jti = Column(String(36), unique=True, nullable=False, index=True)  # JWT ID from refresh token
    
    # User Information
    user_id = Column(Integer, nullable=False, index=True)
    user_type = Column(String(10), nullable=False)  # 'lawyer' or 'admin'
    
    # Session Details
    created_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    last_activity = Column(TIMESTAMP, default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Device Information
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=True)
    device_type = Column(String(20), nullable=True)  # mobile, desktop, tablet
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    
    # Location (Optional)
    country_code = Column(String(2), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Session Context
    login_method = Column(String(20), nullable=True)  # password, mfa, oauth
    
    __table_args__ = (
        Index('idx_user_active', 'user_id', 'user_type', 'is_active'),
        Index('idx_expires_at', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<ActiveSession(user_id={self.user_id}, jti='{self.jti[:8]}...', ip='{self.ip_address}')>"