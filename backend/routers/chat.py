from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.config import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatSessionWithMessages,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryQuery,
    ChatSendMessage,
    ChatExchangeResponse,
    ChatHistoryItem
)
from schemas.messages import UserQuery
from services.chat_service import ChatService

# Import your AI chain/agent here
from chains import invoke_chain

router = APIRouter(prefix="/chat", tags=["chat"])

# ============================================================================
# Main Chat Endpoint (Auto-saves history like ChatGPT)
# ============================================================================

@router.post("/send", response_model=ChatExchangeResponse)
async def send_chat_message(
    chat_data: ChatSendMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message and get AI response. Automatically saves both to history.
    If session_id is not provided, creates a new session.
    """
    try:
        # Get or create session
        session = ChatService.get_or_create_session(
            db=db,
            user_id=current_user.id,
            session_id=chat_data.session_id,
            title="New Chat"
        )
        
        # Get AI response using your existing chain
        try:
            # Create UserQuery object for the chain
            user_query = UserQuery(question=chat_data.message)
            ai_response = invoke_chain(user_query)
            # Handle both SynthesizerOutput and RefusalOutput
            if hasattr(ai_response, 'answer'):
                assistant_message = ai_response.answer
            elif hasattr(ai_response, 'response'):
                assistant_message = ai_response.response
            elif hasattr(ai_response, 'reason'):
                assistant_message = ai_response.reason
            else:
                assistant_message = str(ai_response)
        except Exception as e:
            # Fallback response if AI chain fails (validation errors, etc.)
            assistant_message = "I apologize, but I'm having trouble processing your request right now. Please try again."
            # Only log the error, don't expose internal details to user
            import logging
            logging.warning(f"AI Chain Error: {type(e).__name__}: {str(e)[:100]}")
        
        # Save both messages to database
        user_msg, assistant_msg = ChatService.save_chat_exchange(
            db=db,
            user_id=current_user.id,
            session_id=session.id,
            user_message=chat_data.message,
            assistant_message=assistant_message,
            user_metadata=chat_data.metadata,
            assistant_metadata={"model": "gpt-4", "tokens": len(assistant_message.split())}
        )
        
        # Refresh session to get updated data
        db.refresh(session)
        
        # Convert to response models (messages are already dicts)
        return ChatExchangeResponse(
            session_id=session.id,
            user_message=ChatMessageResponse(**user_msg),
            assistant_message=ChatMessageResponse(**assistant_msg),
            session=ChatSessionResponse.model_validate(session)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )

@router.get("/history", response_model=List[ChatHistoryItem])
def get_chat_history(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get chat history for sidebar display (like ChatGPT).
    Returns list of sessions ordered by most recent.
    """
    sessions = ChatService.get_user_sessions(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return [
        ChatHistoryItem(
            id=session.id,
            title=session.title,
            last_message=session.last_message,
            message_count=session.message_count,
            updated_at=session.updated_at,
            created_at=session.created_at
        )
        for session in sessions
    ]

# ============================================================================
# Chat Sessions
# ============================================================================

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat session"""
    session = ChatService.create_session(
        db=db,
        user_id=current_user.id,
        title=session_data.title
    )
    return session

@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_chat_sessions(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chat sessions for the current user"""
    sessions = ChatService.get_user_sessions(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    return sessions

@router.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
def get_chat_session(
    session_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat session with messages"""
    session = ChatService.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = ChatService.get_session_messages(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    # Convert dicts to ChatMessageResponse models
    message_responses = [ChatMessageResponse(**msg) for msg in messages]
    
    return ChatSessionWithMessages(
        **ChatSessionResponse.model_validate(session).model_dump(),
        messages=message_responses
    )

@router.patch("/sessions/{session_id}", response_model=ChatSessionResponse)
def update_chat_session(
    session_id: UUID,
    update_data: ChatSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a chat session (e.g., rename)"""
    session = ChatService.update_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
        update_data=update_data
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a chat session and all its messages"""
    success = ChatService.delete_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return None

# ============================================================================
# Chat Messages
# ============================================================================

@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def create_chat_message(
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new chat message"""
    # Verify session exists and belongs to user
    session = ChatService.get_session(db, message_data.session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    message = ChatService.create_message(
        db=db,
        user_id=current_user.id,
        message_data=message_data
    )
    return message

@router.get("/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    session_id: UUID = None,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat messages with optional filters"""
    query = ChatHistoryQuery(
        session_id=session_id,
        limit=limit,
        offset=offset
    )
    
    messages = ChatService.get_user_messages(
        db=db,
        user_id=current_user.id,
        query=query
    )
    return messages

@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific chat message"""
    success = ChatService.delete_message(
        db=db,
        message_id=message_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat message not found"
        )
    
    return None

@router.get("/stats")
def get_chat_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat statistics for the current user"""
    session_count = ChatService.get_session_count(db, current_user.id)
    
    return {
        "total_sessions": session_count,
        "user_id": current_user.id
    }
