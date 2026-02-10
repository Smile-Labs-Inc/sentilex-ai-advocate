from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from datetime import datetime
import json
import asyncio

from models.notification import Notification, RecipientTypeEnum, NotificationTypeEnum


class NotificationService(ABC):
    """
    Abstract base class for notification services.
    
    Benefits of Interface Pattern:
    1. **SOLID Principles**: Follows Interface Segregation and Dependency Inversion
    2. **Testability**: Easy to mock for unit tests
    3. **Extensibility**: Can add new notification channels (SMS, Push, Email)
    4. **Consistency**: Ensures all implementations have the same contract
    5. **Flexibility**: Can switch implementations without changing client code
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    @abstractmethod
    def get_recipient_type(self) -> RecipientTypeEnum:
        """Get the recipient type this service handles"""
        pass
    
    def send(
        self, 
        recipient_id: int, 
        message: str,
        title: Optional[str] = None,
        notification_type: NotificationTypeEnum = NotificationTypeEnum.SYSTEM,
        priority: int = 1,
        action_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None
    ) -> Notification:
        """
        Send a notification to the recipient.
        
        Args:
            recipient_id: ID of the recipient
            message: Notification content
            title: Optional title/heading
            notification_type: Type of notification
            priority: Priority level (1=low, 2=medium, 3=high)
            action_url: Optional deep link
            metadata: Optional additional data
            expires_at: Optional expiration time
            
        Returns:
            Created notification instance
        """
        notification = Notification(
            recipient_id=recipient_id,
            recipient_type=self.get_recipient_type(),
            title=title,
            message=message,
            type=notification_type,
            priority=priority,
            action_url=action_url,
            metadata_json=json.dumps(metadata) if metadata else None,
            expires_at=expires_at
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Hook for subclasses to implement additional logic
        self._post_send_hook(notification)
        
        # Send WebSocket notification asynchronously
        try:
            # Import here to avoid circular imports
            from services.websocket_manager import get_notification_manager
            manager = get_notification_manager()
            
            # Schedule the WebSocket notification to be sent
            import threading
            def send_websocket():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(manager.send_notification(notification))
                    loop.close()
                except Exception as e:
                    print(f"WebSocket send error: {e}")
            
            # Run in background thread to avoid blocking
            thread = threading.Thread(target=send_websocket)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            # Don't let WebSocket errors break the notification creation
            print(f"Warning: Failed to send WebSocket notification: {e}")
        
        return notification
    
    def mark_as_read(self, notification_id: int, recipient_id: int) -> bool:
        """
        Mark notification as read (with recipient verification).
        
        Args:
            notification_id: ID of the notification
            recipient_id: ID of the recipient (for security)
            
        Returns:
            True if marked successfully, False otherwise
        """
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.recipient_id == recipient_id,
            Notification.recipient_type == self.get_recipient_type(),
            Notification.is_deleted == False
        ).first()
        
        if notification:
            notification.mark_as_read()
            self.db.commit()
            return True
        return False
    
    def get_unread(
        self, 
        recipient_id: int, 
        limit: Optional[int] = None
    ) -> List[Notification]:
        """Get unread notifications for recipient"""
        query = self.db.query(Notification).filter(
            Notification.recipient_id == recipient_id,
            Notification.recipient_type == self.get_recipient_type(),
            Notification.is_read == False,
            Notification.is_deleted == False
        ).order_by(Notification.created_at.desc())
        
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    def get_all(
        self, 
        recipient_id: int,
        page: int = 1,
        page_size: int = 20,
        notification_type: Optional[NotificationTypeEnum] = None,
        include_read: bool = True
    ) -> Dict[str, Any]:
        """
        Get all notifications for recipient with pagination.
        
        Returns:
            Dict with 'notifications', 'total', 'page', 'pages' keys
        """
        query = self.db.query(Notification).filter(
            Notification.recipient_id == recipient_id,
            Notification.recipient_type == self.get_recipient_type(),
            Notification.is_deleted == False
        )
        
        if notification_type:
            query = query.filter(Notification.type == notification_type)
            
        if not include_read:
            query = query.filter(Notification.is_read == False)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        notifications = query.order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(page_size).all()
        
        pages = (total + page_size - 1) // page_size
        
        return {
            'notifications': notifications,
            'total': total,
            'page': page,
            'pages': pages,
            'page_size': page_size
        }
    
    def get_unread_count(self, recipient_id: int) -> int:
        """Get count of unread notifications"""
        return self.db.query(Notification).filter(
            Notification.recipient_id == recipient_id,
            Notification.recipient_type == self.get_recipient_type(),
            Notification.is_read == False,
            Notification.is_deleted == False
        ).count()
    
    def soft_delete(self, notification_id: int, recipient_id: int) -> bool:
        """Soft delete a notification (with recipient verification)"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.recipient_id == recipient_id,
            Notification.recipient_type == self.get_recipient_type()
        ).first()
        
        if notification:
            notification.soft_delete()
            self.db.commit()
            return True
        return False
    
    def mark_all_as_read(self, recipient_id: int) -> int:
        """Mark all unread notifications as read. Returns count of updated notifications."""
        notifications = self.db.query(Notification).filter(
            Notification.recipient_id == recipient_id,
            Notification.recipient_type == self.get_recipient_type(),
            Notification.is_read == False,
            Notification.is_deleted == False
        ).all()
        
        count = 0
        current_time = datetime.utcnow()
        for notification in notifications:
            notification.is_read = True
            notification.read_at = current_time
            count += 1
            
        self.db.commit()
        return count
    
    def _post_send_hook(self, notification: Notification) -> None:
        """
        Hook method for subclasses to implement additional logic after sending.
        Examples: Send email, push notification, WebSocket broadcast, etc.
        """
        pass


class UserNotificationService(NotificationService):
    """Notification service for regular users"""
    
    def get_recipient_type(self) -> RecipientTypeEnum:
        return RecipientTypeEnum.USER
    
    def _post_send_hook(self, notification: Notification) -> None:
        """User-specific post-send logic"""
        # Could implement: Email notifications, mobile push, etc.
        pass
    
    def send_case_update(
        self, 
        user_id: int, 
        case_title: str, 
        status: str,
        case_id: Optional[int] = None
    ) -> Notification:
        """Convenience method for case updates"""
        title = f"Case Update: {case_title}"
        message = f"Your case status has been updated to: {status}"
        action_url = f"/cases/{case_id}" if case_id else None
        
        return self.send(
            recipient_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationTypeEnum.CASE_UPDATE,
            priority=2,
            action_url=action_url
        )


class LawyerNotificationService(NotificationService):
    """Notification service for lawyers"""
    
    def get_recipient_type(self) -> RecipientTypeEnum:
        return RecipientTypeEnum.LAWYER
    
    def _post_send_hook(self, notification: Notification) -> None:
        """Lawyer-specific post-send logic"""
        # Could implement: Professional email notifications, SMS for urgent cases
        pass
    
    def send_verification_update(
        self, 
        lawyer_id: int, 
        status: str, 
        next_step: Optional[str] = None
    ) -> Notification:
        """Convenience method for verification updates"""
        if status == "approved":
            title = "🎉 Verification Approved"
            message = "Congratulations! Your lawyer verification has been approved. You can now accept cases."
            priority = 3
        elif status == "rejected":
            title = "❌ Verification Rejected"
            message = f"Your verification was rejected. {next_step or 'Please review and resubmit.'}"
            priority = 3
        else:
            title = f"Verification Update"
            message = f"Your verification status: {status}. {next_step or ''}"
            priority = 2
        
        return self.send(
            recipient_id=lawyer_id,
            title=title,
            message=message,
            notification_type=NotificationTypeEnum.VERIFICATION,
            priority=priority,
            action_url="/profile/verification"
        )
    
    def send_new_case_assignment(
        self, 
        lawyer_id: int, 
        case_title: str, 
        case_id: int,
        client_name: str
    ) -> Notification:
        """Notify lawyer of new case assignment"""
        title = f"New Case Assignment: {case_title}"
        message = f"You have been assigned a new case from {client_name}. Please review and respond promptly."
        
        return self.send(
            recipient_id=lawyer_id,
            title=title,
            message=message,
            notification_type=NotificationTypeEnum.CASE_UPDATE,
            priority=3,
            action_url=f"/lawyer/cases/{case_id}",
            metadata={"case_id": case_id, "client_name": client_name}
        )


class AdminNotificationService(NotificationService):
    """Notification service for administrators (future extensibility)"""
    
    def get_recipient_type(self) -> RecipientTypeEnum:
        return RecipientTypeEnum.ADMIN
    
    def send_system_alert(
        self, 
        admin_id: int, 
        alert_type: str, 
        details: str
    ) -> Notification:
        """Send system alerts to administrators"""
        title = f"System Alert: {alert_type}"
        
        return self.send(
            recipient_id=admin_id,
            title=title,
            message=details,
            notification_type=NotificationTypeEnum.SYSTEM,
            priority=3
        )


# Factory function for creating appropriate notification service
def create_notification_service(
    recipient_type: Union[RecipientTypeEnum, str], 
    db_session: Session
) -> NotificationService:
    """
    Factory function to create the appropriate notification service.
    
    Benefits:
    1. Centralized service creation logic
    2. Easy to extend with new recipient types
    3. Type safety and validation
    """
    if isinstance(recipient_type, str):
        recipient_type = RecipientTypeEnum(recipient_type)
    
    service_map = {
        RecipientTypeEnum.USER: UserNotificationService,
        RecipientTypeEnum.LAWYER: LawyerNotificationService,
        RecipientTypeEnum.ADMIN: AdminNotificationService,
    }
    
    service_class = service_map.get(recipient_type)
    if not service_class:
        raise ValueError(f"No notification service available for recipient type: {recipient_type}")
    
    return service_class(db_session)