from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.sql import func
from database.config import Base

class LawyerVerificationAudit(Base):
    '''Immutable audit log for all verification actions'''
    __tablename__ = "lawyer_verification_audit"

    id = Column(Integer, primary_key=True, index=True)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    step_number = Column(Integer, nullable=True)
    performed_by = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
