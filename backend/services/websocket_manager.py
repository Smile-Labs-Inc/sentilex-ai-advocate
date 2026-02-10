"""
WebSocket Notification Manager
Handles real-time notification delivery to frontend clients
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from models.notification import RecipientTypeEnum, Notification
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # Store active connections by user type and ID
        self.active_connections: Dict[str, Dict[int, WebSocket]] = {
            "user": {},
            "lawyer": {},
            "admin": {}
        }
    
    async def connect(self, websocket: WebSocket, user_type: str, user_id: int):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Store the connection
        if user_type not in self.active_connections:
            self.active_connections[user_type] = {}
        
        # Close any existing connection for this user
        if user_id in self.active_connections[user_type]:
            try:
                await self.active_connections[user_type][user_id].close()
            except:
                pass
        
        self.active_connections[user_type][user_id] = websocket
        logger.info(f"WebSocket connected: {user_type}:{user_id}")
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Real-time notifications enabled"
        }, user_type, user_id)
    
    def disconnect(self, user_type: str, user_id: int):
        """Remove a WebSocket connection"""
        if (user_type in self.active_connections and 
            user_id in self.active_connections[user_type]):
            del self.active_connections[user_type][user_id]
            logger.info(f"WebSocket disconnected: {user_type}:{user_id}")
    
    async def send_personal_message(self, message: dict, user_type: str, user_id: int):
        """Send message to a specific user"""
        if (user_type in self.active_connections and 
            user_id in self.active_connections[user_type]):
            try:
                websocket = self.active_connections[user_type][user_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send WebSocket message to {user_type}:{user_id}: {e}")
                # Remove the connection if it's broken
                self.disconnect(user_type, user_id)
    
    async def broadcast_to_user_type(self, message: dict, user_type: str):
        """Broadcast message to all users of a specific type"""
        if user_type in self.active_connections:
            disconnect_list = []
            
            for user_id, websocket in self.active_connections[user_type].items():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to broadcast to {user_type}:{user_id}: {e}")
                    disconnect_list.append(user_id)
            
            # Remove broken connections
            for user_id in disconnect_list:
                self.disconnect(user_type, user_id)
    
    async def send_notification(self, notification: Notification):
        """Send a notification via WebSocket"""
        user_type_mapping = {
            RecipientTypeEnum.USER: "user",
            RecipientTypeEnum.LAWYER: "lawyer",
            RecipientTypeEnum.ADMIN: "admin"
        }
        
        user_type = user_type_mapping.get(notification.recipient_type)
        if not user_type:
            return
        
        message = {
            "type": "notification",
            "data": {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.type.value,
                "priority": notification.priority,
                "action_url": notification.action_url,
                "created_at": notification.created_at.isoformat(),
                "is_read": notification.is_read,
                "metadata": json.loads(notification.metadata_json) if notification.metadata_json else None
            }
        }
        
        await self.send_personal_message(message, user_type, notification.recipient_id)
    
    def get_connection_count(self) -> Dict[str, int]:
        """Get the number of active connections by user type"""
        return {
            user_type: len(connections)
            for user_type, connections in self.active_connections.items()
        }


# Global connection manager instance
notification_manager = ConnectionManager()


def get_notification_manager() -> ConnectionManager:
    """Get the global notification manager instance"""
    return notification_manager