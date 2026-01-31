from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, Boolean, Text, Enum, func
from database.config import Base
import enum

class VerificationStatusEnum(enum.Enum):
    not_started = "not_started"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class AvailabilityEnum(str, enum.Enum):
    AVAILABLE = "Available"
    BUSY = "Busy"
    OFFLINE = "Offline"

class VerificationStatusEnum(str, enum.Enum):
    not_started = "not_started"
    submitted = "submitted"
    in_progress = "in_progress"
    approved = "approved"
    rejected = "rejected"

class Lawyer(Base):
    __tablename__ = "lawyers"

    # Primary Information
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialties = Column(String(255), nullable=True)  # Nullable for OAuth users
    experience_years = Column(Integer, nullable=True)  # Nullable for OAuth users
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)  # Nullable for OAuth users
    district = Column(String(50), nullable=True)  # Nullable for OAuth users
    availability = Column(String(50), default="Available")
    rating = Column(DECIMAL(2,1), default=0.0)
    reviews_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=func.now())
    
    # Profile Completion (for OAuth users)
    profile_completed = Column(Boolean, default=False)  # True if all required fields filled
    
    # Authentication & Security
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    oauth_provider = Column(String(20), nullable=True)  # e.g. "google"
    oauth_id = Column(String(255), nullable=True)  # Google sub ID
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_sent_at = Column(TIMESTAMP, nullable=True)
    
    # Password Security
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(TIMESTAMP, nullable=True)
    password_changed_at = Column(TIMESTAMP, nullable=True)
    password_history = Column(Text, nullable=True)  # JSON array of last 5 password hashes
    
    # Login Security
    last_login = Column(TIMESTAMP, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 support
    last_login_user_agent = Column(Text, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(TIMESTAMP, nullable=True)
    
    # Multi-Factor Authentication (Optional for lawyers)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(32), nullable=True)  # TOTP secret
    mfa_backup_codes = Column(Text, nullable=True)  # Encrypted JSON array of backup codes
    mfa_enabled_at = Column(TIMESTAMP, nullable=True)
    
    # Session Management
    active_sessions = Column(Integer, default=0, nullable=False)
    max_concurrent_sessions = Column(Integer, default=5, nullable=False)  # Lawyers can have more devices

    verification_step = Column(Integer, default=1, nullable=False)
    verification_status = Column(
        Enum(VerificationStatusEnum), 
        default=VerificationStatusEnum.not_started,
        nullable=False
    )

    verification_submitted_at = Column(TIMESTAMP, nullable=True)
    verification_updated_at = Column(TIMESTAMP, onupdate=func.now(), nullable=True)

    sc_enrollment_number = Column(String(50), unique=True, nullable=True, index=True)
    enrollment_year = Column(Integer, nullable=True)
    law_college_reg_number = Column(String(50), nullable=True)
    

    nic_front_url = Column(String(500), nullable=True)
    nic_front_hash = Column(String(64), nullable=True)  
    nic_front_uploaded_at = Column(TIMESTAMP, nullable=True)
    
    nic_back_url = Column(String(500), nullable=True)
    nic_back_hash = Column(String(64), nullable=True)
    nic_back_uploaded_at = Column(TIMESTAMP, nullable=True)
    
    attorney_certificate_url = Column(String(500), nullable=True)
    attorney_certificate_hash = Column(String(64), nullable=True)
    attorney_certificate_uploaded_at = Column(TIMESTAMP, nullable=True)
    
    practising_certificate_url = Column(String(500), nullable=True)
    practising_certificate_hash = Column(String(64), nullable=True)
    practising_certificate_uploaded_at = Column(TIMESTAMP, nullable=True)
    
    
    declaration_accepted = Column(Boolean, default=False, nullable=False)
    declaration_accepted_at = Column(TIMESTAMP, nullable=True)
    declaration_ip_address = Column(String(45), nullable=True)  
    
    verified_by_admin_id = Column(Integer, nullable=True)  
    verified_at = Column(TIMESTAMP, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Lawyer(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    @property
    def is_locked(self) -> bool:
        """Check if account is currently locked"""
        if not self.locked_until:
            return False
        from datetime import datetime
        return datetime.utcnow() < self.locked_until
    
    @property
    def is_verified(self) -> bool:
        """Check if lawyer has completed verification"""
        return self.verification_status == VerificationStatusEnum.approved
    
    @property
    def can_login(self) -> bool:
        """Check if lawyer can log in (active, verified email, not locked)"""
        return (
            self.is_active and 
            self.is_email_verified and 
            not self.is_locked and
            self.password_hash is not None
        )