from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime

from models.session_chat import SessionChatMessage, ChatSession
from schemas.chat import (
    ChatMessageCreate, 
    ChatSessionCreate, 
    ChatSessionUpdate,
    ChatHistoryQuery
)

class ChatService:
    """Service for managing chat messages and sessions"""
    
    @staticmethod
    def get_or_create_session(
        db: Session, 
        user_id: int, 
        session_id: Optional[UUID] = None,
        title: str = "New Chat"
    ) -> ChatSession:
        """Get existing session or create new one"""
        if session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()
            if session:
                return session
        
        # Create new session
        session = ChatSession(
            user_id=user_id,
            title=title,
            message_count=0
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def save_chat_exchange(
        db: Session,
        user_id: int,
        session_id: UUID,
        user_message: str,
        assistant_message: str,
        user_metadata: dict = None,
        assistant_metadata: dict = None
    ) -> Tuple[dict, dict]:
        """Save both user message and assistant response in one transaction.
        Returns dicts instead of model objects to avoid session expiration issues."""
        
        from datetime import datetime, timezone
        
        # Store creation timestamp with timezone
        now = datetime.now(timezone.utc)
        
        # Create user message
        user_msg = SessionChatMessage(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=user_message,
            message_metadata=user_metadata or {},
            created_at=now
        )
        
        db.add(user_msg)
        db.flush()  # Flush to get the ID before adding second message
        
        # Create assistant message with slightly different timestamp to avoid PK conflict
        assistant_now = datetime.now(timezone.utc)
        assistant_msg = SessionChatMessage(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=assistant_message,
            message_metadata=assistant_metadata or {},
            created_at=assistant_now
        )
        
        db.add(assistant_msg)
        
        # Update session metadata
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        
        if session:
            session.message_count += 2  # Both user and assistant messages
            session.last_message = assistant_message[:200]
            session.updated_at = func.now()
            
            # Auto-generate title from first user message if still "New Chat"
            if session.title == "New Chat" and session.message_count == 2:
                # Use first 50 chars of user message as title
                session.title = user_message[:50].strip()
                if len(user_message) > 50:
                    session.title += "..."
        
        db.commit()
        
        # Refresh to get the generated IDs
        db.refresh(user_msg)
        db.refresh(assistant_msg)
        
        # Return dicts
        user_msg_dict = {
            'id': user_msg.id,
            'session_id': session_id,
            'user_id': user_id,
            'role': "user",
            'content': user_message,
            'metadata': user_metadata or {},
            'created_at': user_msg.created_at
        }
        
        assistant_msg_dict = {
            'id': assistant_msg.id,
            'session_id': session_id,
            'user_id': user_id,
            'role': "assistant",
            'content': assistant_message,
            'metadata': assistant_metadata or {},
            'created_at': assistant_msg.created_at
        }
        
        return user_msg_dict, assistant_msg_dict
    
    @staticmethod
    def create_session(db: Session, user_id: int, title: str) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            user_id=user_id,
            title=title,
            message_count=0
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: UUID, user_id: int) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        return db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_sessions(
        db: Session, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ChatSession]:
        """Get all chat sessions for a user"""
        return db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(
            desc(ChatSession.updated_at)
        ).limit(limit).offset(offset).all()
    
    @staticmethod
    def update_session(
        db: Session, 
        session_id: UUID, 
        user_id: int, 
        update_data: ChatSessionUpdate
    ) -> Optional[ChatSession]:
        """Update a chat session"""
        session = ChatService.get_session(db, session_id, user_id)
        if not session:
            return None
        
        if update_data.title:
            session.title = update_data.title
        
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def delete_session(db: Session, session_id: UUID, user_id: int) -> bool:
        """Delete a chat session and all its messages"""
        session = ChatService.get_session(db, session_id, user_id)
        if not session:
            return False
        
        # Delete all messages in the session
        db.query(SessionChatMessage).filter(
            SessionChatMessage.session_id == session_id
        ).delete()
        
        db.delete(session)
        db.commit()
        return True
    
    @staticmethod
    def create_message(
        db: Session, 
        user_id: int, 
        message_data: ChatMessageCreate
    ) -> SessionChatMessage:
        """Create a new chat message"""
        message = SessionChatMessage(
            user_id=user_id,
            session_id=message_data.session_id,
            role=message_data.role,
            content=message_data.content,
            metadata=message_data.metadata or {}
        )
        db.add(message)
        
        # Update session metadata
        session = db.query(ChatSession).filter(
            ChatSession.id == message_data.session_id
        ).first()
        
        if session:
            session.message_count += 1
            session.last_message = message_data.content[:200]  # Store preview
            session.updated_at = func.now()
        
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def get_session_messages(
        db: Session,
        session_id: UUID,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[dict]:
        """Get messages for a specific session, returns dicts to avoid metadata attribute conflicts"""
        messages = db.query(SessionChatMessage).filter(
            SessionChatMessage.session_id == session_id,
            SessionChatMessage.user_id == user_id
        ).order_by(
            SessionChatMessage.created_at.asc()
        ).limit(limit).offset(offset).all()
        
        # Convert to dicts to avoid SQLAlchemy metadata conflicts
        return [
            {
                'id': msg.id,
                'session_id': msg.session_id,
                'user_id': msg.user_id,
                'role': msg.role,
                'content': msg.content,
                'metadata': msg.message_metadata or {},  # Use message_metadata attribute
                'created_at': msg.created_at
            }
            for msg in messages
        ]
    
    @staticmethod
    def get_user_messages(
        db: Session,
        user_id: int,
        query: ChatHistoryQuery
    ) -> List[SessionChatMessage]:
        """Get chat messages for a user with filters"""
        filters = [SessionChatMessage.user_id == user_id]
        
        if query.session_id:
            filters.append(SessionChatMessage.session_id == query.session_id)
        
        if query.start_date:
            filters.append(SessionChatMessage.created_at >= query.start_date)
        
        if query.end_date:
            filters.append(SessionChatMessage.created_at <= query.end_date)
        
        return db.query(SessionChatMessage).filter(
            *filters
        ).order_by(
            desc(SessionChatMessage.created_at)
        ).limit(query.limit).offset(query.offset).all()
    
    @staticmethod
    def delete_message(db: Session, message_id: int, user_id: int) -> bool:
        """Delete a specific chat message"""
        message = db.query(SessionChatMessage).filter(
            SessionChatMessage.id == message_id,
            SessionChatMessage.user_id == user_id
        ).first()
        
        if not message:
            return False
        
        session_id = message.session_id
        db.delete(message)
        
        # Update session message count
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id
        ).first()
        
        if session and session.message_count > 0:
            session.message_count -= 1
        
        db.commit()
        return True
    
    @staticmethod
    def get_session_count(db: Session, user_id: int) -> int:
        """Get total number of sessions for a user"""
        return db.query(func.count(ChatSession.id)).filter(
            ChatSession.user_id == user_id
        ).scalar()
