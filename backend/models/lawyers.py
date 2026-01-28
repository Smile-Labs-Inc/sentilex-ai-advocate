from sqlalchemy import Column, Integer, String, Enum, DECIMAL, TIMESTAMP, Boolean, Text
from sqlalchemy.sql import func
from database.config import Base
import enum

class AvailabilityEnum(enum.Enum):
    Available = "Available"
    InConsultation = "In Consultation"
    Offline = "Offline"

class VerificationStatusEnum(enum.Enum):
    not_started = "not Started"
    in_progress = "in Progress"
    submitted = "submitted" 
    approved = "approved"
    rejected = "rejected"

class Lawyer(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    specialties = Column(String(255), nullable=False)
    experience_years = Column(Integer, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    district = Column(String(50), nullable=False)
    availability = Column(Enum(AvailabilityEnum), default=AvailabilityEnum.Available)
    rating = Column(DECIMAL(2,1), default=0.0)
    reviews_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP)

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