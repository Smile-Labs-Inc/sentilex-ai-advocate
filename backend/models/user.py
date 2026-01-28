from sqlalchemy import Column, Integer, String, Boolean, Enum, TIMESTAMP
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
    role = Column(Enum("user", "lawyer", "admin"), default="user")
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)

    # Security
    mfa_enabled = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    last_login_at = Column(TIMESTAMP, nullable=True)

    # Preferences
    preferred_language = Column(Enum("si", "ta", "en"), default="en")
    district = Column(String(50))
