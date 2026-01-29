"""
Login Attempt Tracking Model

Tracks failed login attempts for rate limiting and security monitoring.
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Index
from sqlalchemy.sql import func
from database.config import Base


class LoginAttempt(Base):
    """
    Track login attempts for security monitoring and rate limiting.
    
    Records both successful and failed login attempts with IP and user agent.
    Used for:
    - Account lockout after repeated failures
    - Suspicious activity detection
    - Security audit trail
    """
    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    
    # User Information
    email = Column(String(100), nullable=False, index=True)
    user_type = Column(String(10), nullable=False)  # 'lawyer' or 'admin'
    user_id = Column(Integer, nullable=True)  # Null if user doesn't exist
    
    # Attempt Details
    success = Column(Boolean, nullable=False)
    attempted_at = Column(TIMESTAMP, default=func.now(), nullable=False, index=True)
    
    # Network Information
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(String(500), nullable=True)
    
    # Failure Details
    failure_reason = Column(String(100), nullable=True)  # wrong_password, account_locked, user_not_found, mfa_failed, etc.
    
    # Additional Context
    country_code = Column(String(2), nullable=True)  # For geolocation analysis
    is_suspicious = Column(Boolean, default=False, nullable=False)  # Flagged by security rules
    
    __table_args__ = (
        Index('idx_email_attempted', 'email', 'attempted_at'),
        Index('idx_ip_attempted', 'ip_address', 'attempted_at'),
        Index('idx_user_attempted', 'user_id', 'attempted_at'),
    )
    
    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"<LoginAttempt(email='{self.email}', {status}, ip='{self.ip_address}')>"
