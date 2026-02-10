"""
Memory Classes for Case Agent

Per-incident and global user chat history implementations.
"""

from typing import List
from sqlalchemy.orm import Session
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from models.incident_chat import IncidentChatMessage


class IncidentChatHistory(BaseChatMessageHistory):
    """Per-incident case memory."""
    
    def __init__(self, incident_id: int, session: Session):
        self.incident_id = incident_id
        self.session = session

    @property
    def messages(self) -> List[BaseMessage]:
        rows = (
            self.session.query(IncidentChatMessage)
            .filter(IncidentChatMessage.incident_id == self.incident_id)
            .order_by(IncidentChatMessage.created_at.asc())
            .all()
        )
        return [
            HumanMessage(content=r.content) if r.role.value == "user" 
            else AIMessage(content=r.content) 
            for r in rows
        ]

    def add_message(self, message: BaseMessage) -> None:
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        row = IncidentChatMessage(
            incident_id=self.incident_id, 
            role=role, 
            content=message.content
        )
        self.session.add(row)
        self.session.commit()

    def clear(self) -> None:
        """Clear all messages for this incident."""
        self.session.query(IncidentChatMessage).filter(
            IncidentChatMessage.incident_id == self.incident_id
        ).delete()
        self.session.commit()


class UserGlobalChatHistory(BaseChatMessageHistory):
    """Global cross-incident user memory."""
    
    def __init__(self, user_id: int, session: Session):
        self.user_id = user_id
        self.session = session

    @property
    def messages(self) -> List[BaseMessage]:
        rows = (
            self.session.query(IncidentChatMessage)
            .filter(IncidentChatMessage.user_id == self.user_id)
            .order_by(IncidentChatMessage.created_at.asc())
            .all()
        )
        return [
            HumanMessage(content=r.content) if r.role.value == "user" 
            else AIMessage(content=r.content) 
            for r in rows
        ]

    def add_message(self, message: BaseMessage) -> None:
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        row = IncidentChatMessage(
            user_id=self.user_id, 
            role=role, 
            content=message.content
        )
        self.session.add(row)
        self.session.commit()

    def clear(self) -> None:
        """Clear all messages for this user."""
        self.session.query(IncidentChatMessage).filter(
            IncidentChatMessage.user_id == self.user_id
        ).delete()
        self.session.commit()
