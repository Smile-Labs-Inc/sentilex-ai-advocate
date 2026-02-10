from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Union
import logging

from database.config import get_db
from models.notification import RecipientTypeEnum, NotificationTypeEnum
from schemas.notification import (
    SendNotificationRequest, NotificationResponse, NotificationListResponse,
    UnreadCountResponse, BulkActionResponse, NotificationStatsResponse,
    SendNotificationResponse, MarkAsReadRequest, NotificationQueryParams
)
from services.notification_service import create_notification_service
from auth.dependencies import get_current_user, get_current_lawyer, get_current_admin

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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
    current_user = Depends(get_current_user),
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