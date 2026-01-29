"""
Token Blacklist Model for JWT Token Revocation

Tracks revoked tokens for logout, password changes, and security events.
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, Index
from sqlalchemy.sql import func
from database.config import Base


class TokenBlacklist(Base):
    """
    Token blacklist for handling logout and security events.
    
    When a user logs out or changes password, their tokens are added here.
    Tokens are checked against this list during authentication.
    """
    __tablename__ = "token_blacklist"

    # Token Identification
    jti = Column(String(36), primary_key=True)  # JWT ID (unique token identifier)
    token_type = Column(String(10), nullable=False)  # 'access' or 'refresh'
    
    # User Information
    user_id = Column(Integer, nullable=False, index=True)
    user_type = Column(String(10), nullable=False)  # 'lawyer' or 'admin'
    
    # Blacklist Details
    blacklisted_at = Column(TIMESTAMP, default=func.now(), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)  # Original token expiration
    reason = Column(String(50), nullable=False)  # logout, password_change, security_event, admin_action
    
    # Additional Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    __table_args__ = (
        Index('idx_user_blacklist', 'user_id', 'user_type'),
        Index('idx_expires_at', 'expires_at'),  # For cleanup queries
    )
    
    def __repr__(self):
        return f"<TokenBlacklist(jti='{self.jti}', user_id={self.user_id}, reason='{self.reason}')>"
