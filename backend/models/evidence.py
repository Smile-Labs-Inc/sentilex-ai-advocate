"""
Evidence Model

Database model for tracking uploaded evidence files for incidents.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base


class Evidence(Base):
    """
    Evidence model for storing metadata about uploaded files.
    
    Files are stored in Amazon S3 with AES-256 encryption.
    This model tracks S3 keys, cryptographic hashes, and metadata
    for retrieval and forensic audit trails.
    """
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    
    # Incident association
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    
    # Occurrence association (optional - for evidence linked to specific occurrences)
    occurrence_id = Column(Integer, ForeignKey("occurrences.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # File metadata
    file_name = Column(String(255), nullable=False)
    file_key = Column(String(500), nullable=False)   # S3 object key
    file_hash = Column(String(64), nullable=False)   # SHA-256 hash for forensic audit
    file_type = Column(String(100), nullable=True)   # MIME type
    file_size = Column(Integer, nullable=True)       # Size in bytes
    
    # Timestamp
    uploaded_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="evidence")
    occurrence = relationship("Occurrence", back_populates="evidence")
    
    def __repr__(self):
        return f"<Evidence(id={self.id}, file_name='{self.file_name}', incident_id={self.incident_id})>"
