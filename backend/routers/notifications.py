from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Union
import logging
import json

from database.config import get_db
from models.notification import RecipientTypeEnum, NotificationTypeEnum
from schemas.notification import (
    SendNotificationRequest, NotificationResponse, NotificationListResponse,
    UnreadCountResponse, BulkActionResponse, NotificationStatsResponse,
    SendNotificationResponse, MarkAsReadRequest, NotificationQueryParams
)
from services.notification_service import create_notification_service
from services.websocket_manager import get_notification_manager
from auth.dependencies import get_current_user, get_current_lawyer, get_current_admin, get_optional_current_user
import jwt
import os

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# Helper functions for getting current user info
def get_user_info(current_user=None, current_lawyer=None, current_admin=None):
    """Extract user ID and type from current user context"""
    if current_user:
        return current_user.id, RecipientTypeEnum.USER
    elif current_lawyer:
        return current_lawyer.id, RecipientTypeEnum.LAWYER
    elif current_admin:
        return current_admin.id, RecipientTypeEnum.ADMIN
    else:
        raise HTTPException(status_code=401, detail="Authentication required")


# Public endpoints (for system/admin use)
@router.post("/send", response_model=SendNotificationResponse, status_code=201)
def send_notification(
    request: SendNotificationRequest,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admins can send arbitrary notifications
):
    """
    Send a notification to any recipient.
    
    **Admin only endpoint** for sending system notifications, announcements, etc.
    """
    try:
        service = create_notification_service(request.recipient_type, db)
        
        notification = service.send(
            recipient_id=request.recipient_id,
            message=request.message,
            title=request.title,
            notification_type=request.type,
            priority=request.priority,
            action_url=request.action_url,
            metadata=request.metadata,
            expires_at=request.expires_at
        )
        
        logger.info(f"Notification sent by admin {current_admin.id} to {request.recipient_type}:{request.recipient_id}")
        
        return SendNotificationResponse(
            id=notification.id,
            notification=NotificationResponse.from_orm(notification)
        )
        
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to send notification: {str(e)}")


# User-specific endpoints
@router.get("/my", response_model=NotificationListResponse)
def get_my_notifications(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    type: Optional[NotificationTypeEnum] = Query(None, description="Filter by notification type"),
    include_read: bool = Query(default=True, description="Include read notifications"),
    priority_min: Optional[int] = Query(None, ge=1, le=3, description="Minimum priority level"),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Get current user's notifications with pagination and filtering"""
    try:
        user_id, user_type = get_user_info(current_user, current_lawyer, current_admin)
        service = create_notification_service(user_type, db)
        
        result = service.get_all(
            recipient_id=user_id,
            page=page,
            page_size=page_size,
            notification_type=type,
            include_read=include_read
        )
        
        # Filter by priority if specified
        if priority_min:
            result['notifications'] = [
                n for n in result['notifications'] if n.priority >= priority_min
            ]
            result['total'] = len(result['notifications'])
        
        # Get unread count
        unread_count = service.get_unread_count(user_id)
        
        # Convert to response models
        notifications = [NotificationResponse.from_orm(n) for n in result['notifications']]
        
        return NotificationListResponse(
            notifications=notifications,
            total=result['total'],
            page=result['page'],
            pages=result['pages'],
            page_size=result['page_size'],
            unread_count=unread_count
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch notifications: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my/unread", response_model=List[NotificationResponse])
def get_unread_notifications(
    limit: Optional[int] = Query(default=50, ge=1, le=100, description="Maximum number of notifications"),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Get current user's unread notifications"""
    try:
        user_id, user_type = get_user_info(current_user, current_lawyer, current_admin)
        service = create_notification_service(user_type, db)
        
        notifications = service.get_unread(user_id, limit=limit)
        return [NotificationResponse.from_orm(n) for n in notifications]
        
    except Exception as e:
        logger.error(f"Failed to fetch unread notifications: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my/count", response_model=UnreadCountResponse)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Get count of unread notifications for current user"""
    try:
        user_id, user_type = get_user_info(current_user, current_lawyer, current_admin)
        service = create_notification_service(user_type, db)
        
        unread_count = service.get_unread_count(user_id)
        return UnreadCountResponse(unread_count=unread_count)
        
    except Exception as e:
        logger.error(f"Failed to get unread count: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/my/mark-read", response_model=BulkActionResponse)
def mark_notifications_read(
    request: MarkAsReadRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Mark specific notifications as read"""
    try:
        user_id, user_type = get_user_info(current_user, current_lawyer, current_admin)
        service = create_notification_service(user_type, db)
        
        success_count = 0
        for notification_id in request.notification_ids:
            if service.mark_as_read(notification_id, user_id):
                success_count += 1
        
        return BulkActionResponse(
            success=True,
            count=success_count,
            message=f"Marked {success_count} notifications as read"
        )
        
    except Exception as e:
        logger.error(f"Failed to mark notifications as read: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/my/mark-all-read", response_model=BulkActionResponse)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Mark all notifications as read for current user"""
    try:
        user_id, user_type = get_user_info(current_user, current_lawyer, current_admin)
        service = create_notification_service(user_type, db)
        
        count = service.mark_all_as_read(user_id)
        
        return BulkActionResponse(
            success=True,
            count=count,
            message=f"Marked {count} notifications as read"
        )
        
    except Exception as e:
        logger.error(f"Failed to mark all notifications as read: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/my/{notification_id}", response_model=BulkActionResponse)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Soft delete a specific notification"""
    try:
        user_id, user_type = get_user_info(current_user, current_lawyer, current_admin)
        service = create_notification_service(user_type, db)
        
        if service.soft_delete(notification_id, user_id):
            return BulkActionResponse(
                success=True,
                count=1,
                message="Notification deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete notification: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my/stats", response_model=NotificationStatsResponse)
def get_notification_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Get notification statistics for current user"""
    try:
        user_id, user_type = get_user_info(current_user, current_lawyer, current_admin)
        service = create_notification_service(user_type, db)
        
        # Get all notifications for stats
        all_notifications = service.get_all(user_id, page_size=10000)['notifications']
        
        total_count = len(all_notifications)
        unread_count = len([n for n in all_notifications if not n.is_read])
        read_count = total_count - unread_count
        urgent_count = len([n for n in all_notifications if n.priority >= 3])
        
        # Count by type
        by_type = {}
        for notification_type in NotificationTypeEnum:
            by_type[notification_type.value] = len([
                n for n in all_notifications if n.type == notification_type
            ])
        
        # Count by priority
        by_priority = {"1": 0, "2": 0, "3": 0}
        for n in all_notifications:
            by_priority[str(n.priority)] = by_priority.get(str(n.priority), 0) + 1
        
        return NotificationStatsResponse(
            total_notifications=total_count,
            unread_count=unread_count,
            read_count=read_count,
            by_type=by_type,
            by_priority=by_priority,
            urgent_count=urgent_count
        )
        
    except Exception as e:
        logger.error(f"Failed to get notification stats: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Convenience endpoints for specific notification types
@router.post("/lawyers/{lawyer_id}/verification", response_model=SendNotificationResponse)
def notify_lawyer_verification(
    lawyer_id: int,
    status: str,
    next_step: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Only admins can send verification updates
):
    """Send verification status update to a lawyer"""
    try:
        service = create_notification_service(RecipientTypeEnum.LAWYER, db)
        notification = service.send_verification_update(lawyer_id, status, next_step)
        
        return SendNotificationResponse(
            id=notification.id,
            notification=NotificationResponse.from_orm(notification)
        )
        
    except Exception as e:
        logger.error(f"Failed to send verification notification: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{user_id}/case-update", response_model=SendNotificationResponse)
def notify_case_update(
    user_id: int,
    case_title: str,
    status: str,
    case_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Send case update notification to a user (lawyers and admins only)"""
    try:
        service = create_notification_service(RecipientTypeEnum.USER, db)
        notification = service.send_case_update(user_id, case_title, status, case_id)
        
        return SendNotificationResponse(
            id=notification.id,
            notification=NotificationResponse.from_orm(notification)
        )
        
    except Exception as e:
        logger.error(f"Failed to send case update notification: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Test endpoint for development
@router.post("/test/send", response_model=SendNotificationResponse)
def send_test_notification(
    message: str = "Test notification from backend",
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Send a test notification to the current user (for development/testing)"""
    try:
        user_id, user_type = get_user_info(current_user, current_lawyer, current_admin)
        service = create_notification_service(user_type, db)
        
        notification = service.send(
            recipient_id=user_id,
            message=message,
            title="Test Notification",
            notification_type=NotificationTypeEnum.SYSTEM,
            priority=2
        )
        
        return SendNotificationResponse(
            id=notification.id,
            notification=NotificationResponse.from_orm(notification)
        )
        
    except Exception as e:
        logger.error(f"Failed to send test notification: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# Alias endpoints for frontend compatibility
@router.get("/", response_model=NotificationListResponse)
def get_notifications_alias(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    type: Optional[NotificationTypeEnum] = Query(None, description="Filter by notification type"),
    include_read: bool = Query(default=True, description="Include read notifications"),
    priority_min: Optional[int] = Query(None, ge=1, le=3, description="Minimum priority level"),
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Alias for /my endpoint - Get current user's notifications"""
    return get_my_notifications(page, page_size, type, include_read, priority_min, db, current_user, current_lawyer, current_admin)


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count_alias(
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Alias for /my/count endpoint - Get count of unread notifications"""
    return get_unread_count(db, current_user, current_lawyer, current_admin)


@router.post("/mark-read", response_model=BulkActionResponse)
def mark_notifications_read_alias(
    request: MarkAsReadRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Alias for /my/mark-read endpoint - Mark specific notifications as read"""
    return mark_notifications_read(request, db, current_user, current_lawyer, current_admin)


@router.post("/mark-all-read", response_model=BulkActionResponse)
def mark_all_notifications_read_alias(
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user),
    current_lawyer = Depends(get_current_lawyer),
    current_admin = Depends(get_current_admin)
):
    """Alias for /my/mark-all-read endpoint - Mark all notifications as read"""
    return mark_all_notifications_read(db, current_user, current_lawyer, current_admin)


# WebSocket endpoint for real-time notifications
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    token: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time notifications.
    
    Usage:
    - Connect to: ws://localhost:8000/api/notifications/ws?token=<jwt_token>
    - The token should be the same JWT token used for API authentication
    """
    manager = get_notification_manager()
    
    # Verify JWT token and extract user info
    try:
        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-min-32-chars")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        user_id = payload.get("sub")
        user_type_raw = payload.get("user_type", "user")
        
        # Map user type from JWT to our enum format
        user_type_mapping = {
            "user": "user",
            "lawyer": "lawyer", 
            "admin": "admin"
        }
        user_type = user_type_mapping.get(user_type_raw, "user")
        
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return
            
        # Connect to WebSocket manager
        await manager.connect(websocket, user_type, int(user_id))
        
        try:
            while True:
                # Keep the connection alive and handle any incoming messages
                data = await websocket.receive_text()
                
                # Parse incoming message (for potential future features like marking as read)
                try:
                    message = json.loads(data)
                    
                    # Handle ping/pong for connection health
                    if message.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    
                    # Handle mark as read requests
                    elif message.get("type") == "mark_as_read":
                        notification_id = message.get("notification_id")
                        if notification_id:
                            # Create service and mark as read
                            recipient_type = {
                                "user": RecipientTypeEnum.USER,
                                "lawyer": RecipientTypeEnum.LAWYER,
                                "admin": RecipientTypeEnum.ADMIN
                            }.get(user_type, RecipientTypeEnum.USER)
                            
                            service = create_notification_service(recipient_type, db)
                            success = service.mark_as_read(int(notification_id), int(user_id))
                            
                            await websocket.send_text(json.dumps({
                                "type": "mark_as_read_response",
                                "success": success,
                                "notification_id": notification_id
                            }))
                    
                except json.JSONDecodeError:
                    # Invalid JSON, ignore
                    pass
                    
        except WebSocketDisconnect:
            manager.disconnect(user_type, int(user_id))
            
    except jwt.PyJWTError:
        await websocket.close(code=4001, reason="Invalid token")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Internal error")
        except:
            pass