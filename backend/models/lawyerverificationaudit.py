from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database.config import Base

class LawyerVerificationAudit(Base):
    __tablename__ = "lawyer_verification_audits"

    id = Column(Integer, primary_key=True, index=True)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), nullable=False)
    action = Column(String, nullable=False)
    step_number = Column(Integer, nullable=True)
    performed_by = Column(String, default="lawyer")  # "lawyer" or "admin:{id}"
    ip_address = Column(String, nullable=True)
    details = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    lawyer = relationship("Lawyer", back_populates="audit_logs")
