from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional, List, Dict, Any

class ChatMessageBase(BaseModel):
    """Base schema for chat messages"""
    session_id: UUID4
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=50000)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message"""
    pass

class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response"""
    id: Optional[int] = None  # Optional due to partitioned table limitations
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    """Base schema for chat sessions"""
    title: str = Field(..., min_length=1, max_length=255)

class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a new chat session"""
    pass

class ChatSessionUpdate(BaseModel):
    """Schema for updating chat session"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)

class ChatSessionResponse(ChatSessionBase):
    """Schema for chat session response"""
    id: UUID4
    user_id: int
    last_message: Optional[str]
    message_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionWithMessages(ChatSessionResponse):
    """Schema for chat session with messages"""
    messages: List[ChatMessageResponse]

class ChatHistoryQuery(BaseModel):
    """Schema for querying chat history"""
    session_id: Optional[UUID4] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ChatSendMessage(BaseModel):
    """Schema for sending a chat message"""
    message: str = Field(..., min_length=1, max_length=50000)
    session_id: Optional[UUID4] = None  # If None, creates new session
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatExchangeResponse(BaseModel):
    """Schema for chat exchange response"""
    session_id: UUID4
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    session: ChatSessionResponse

class ChatHistoryItem(BaseModel):
    """Schema for chat history sidebar item (like ChatGPT)"""
    id: UUID4
    title: str
    last_message: Optional[str]
    message_count: int
    updated_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True