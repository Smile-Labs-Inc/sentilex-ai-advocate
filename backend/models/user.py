from sqlalchemy import Column, Integer, String, Boolean, Enum, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Identity
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    # Authentication
    password_hash = Column(String(255), nullable=True)  # nullable for OAuth users
    oauth_provider = Column(String(20), nullable=True)  # e.g. "google"
    oauth_id = Column(String(255), nullable=True)        # Google sub ID

    # Role & Status
    role = Column(Enum("user", "lawyer", "admin", name="user_role"), default="user")
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)

    # Security
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(32), nullable=True)  # TOTP secret
    mfa_backup_codes = Column(Text, nullable=True)  # Comma-separated backup codes
    mfa_enabled_at = Column(TIMESTAMP, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    last_login_at = Column(TIMESTAMP, nullable=True)
    locked_until = Column(TIMESTAMP, nullable=True)
    
    # Password Security
    password_changed_at = Column(TIMESTAMP, nullable=True)
    password_history = Column(Text, nullable=True)  # JSON array of last 5 password hashes

    # Preferences
    preferred_language = Column(Enum("si", "ta", "en", name="language_preference"), default="en")
    district = Column(String(50), nullable=True)  # Nullable for OAuth users
    
    # Profile Completion (for OAuth users)
    profile_completed = Column(Boolean, default=False)  # True if all required fields filled

    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    