from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.config import Base
import uuid

class ChatMessage(Base):
    """
    Chat message model with partitioning support.
    Messages are partitioned by created_at (daily) for efficient querying.
    """
    __tablename__ = 'chat_messages'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSONB, default={}, name='metadata')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, primary_key=True)

    # Relationship
    user = relationship("User", back_populates="chat_messages")

    __table_args__ = (
        Index('ix_chat_messages_session_time', 'session_id', 'created_at'),
        Index('ix_chat_messages_user_time', 'user_id', 'created_at'),
        Index('ix_chat_messages_metadata', 'metadata', postgresql_using='gin'),
        {'extend_existing': True}
    )
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session={self.session_id}, role={self.role})>"



class ChatSession(Base):
    """
    Chat session metadata for organizing conversations.
    Each session represents a distinct conversation thread.
    """
    __tablename__ = 'chat_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    last_message = Column(Text)
    message_count = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="chat_sessions")
    
    __table_args__ = (
        Index('ix_chat_sessions_user_updated', 'user_id', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, title={self.title})>"