"""
Incident Chat Message Model

Database model for storing AI chat conversation history per incident.
"""

from sqlalchemy import Column, Integer, Text, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base
import enum


class IncidentChatRoleEnum(str, enum.Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class IncidentChatMessage(Base):
    """
    IncidentChatMessage model for storing conversation history with AI assistant.
    
    Each message is linked to an incident and optionally to a user
    for persistent case memory and global user patterns.
    """
    __tablename__ = "incident_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    
    # Incident association
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False, index=True)
    
    # User association (for global memory across incidents)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Message details
    role = Column(Enum(IncidentChatRoleEnum, name='incident_msg_role_type'), nullable=False)
    content = Column(Text, nullable=False)
    
    # Timestamp
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="incident_chat_messages")
    user = relationship("User", backref="incident_chat_messages")
    
    def __repr__(self):
        return f"<IncidentChatMessage(id={self.id}, role='{self.role}', incident_id={self.incident_id})>"
