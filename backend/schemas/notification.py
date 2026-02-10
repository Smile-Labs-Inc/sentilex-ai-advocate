from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from models.notification import RecipientTypeEnum, NotificationTypeEnum


# Request Schemas
class SendNotificationRequest(BaseModel):
    """Request schema for sending notifications"""
    recipient_id: int = Field(..., gt=0, description="ID of the notification recipient")
    recipient_type: RecipientTypeEnum = Field(..., description="Type of recipient (USER/LAWYER)")
    title: Optional[str] = Field(None, max_length=200, description="Optional notification title")
    message: str = Field(..., min_length=1, max_length=2000, description="Notification message content")
    type: NotificationTypeEnum = Field(
        default=NotificationTypeEnum.SYSTEM, 
        description="Type of notification"
    )
    priority: int = Field(default=1, ge=1, le=3, description="Priority level (1=low, 2=medium, 3=high)")
    action_url: Optional[str] = Field(None, max_length=500, description="Optional action URL")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration timestamp")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class MarkAsReadRequest(BaseModel):
    """Request schema for marking notifications as read"""
    notification_ids: List[int] = Field(..., min_items=1, description="List of notification IDs to mark as read")


class NotificationQueryParams(BaseModel):
    """Query parameters for fetching notifications"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of notifications per page")
    type: Optional[NotificationTypeEnum] = Field(None, description="Filter by notification type")
    include_read: bool = Field(default=True, description="Include read notifications")
    priority_min: Optional[int] = Field(None, ge=1, le=3, description="Minimum priority level")

    class Config:
        use_enum_values = True


# Response Schemas
class NotificationResponse(BaseModel):
    """Response schema for individual notifications"""
    id: int
    recipient_id: int
    recipient_type: RecipientTypeEnum
    title: Optional[str]
    message: str
    type: NotificationTypeEnum
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    priority: int
    action_url: Optional[str]
    metadata: Optional[Dict[str, Any]] = None
    is_urgent: bool
    is_expired: bool

    @validator('metadata', pre=True)
    def parse_metadata(cls, v):
        """Parse metadata JSON string to dict"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v) if v else None
            except json.JSONDecodeError:
                return None
        return v

    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class NotificationListResponse(BaseModel):
    """Response schema for paginated notification lists"""
    notifications: List[NotificationResponse]
    total: int = Field(..., description="Total number of notifications")
    page: int = Field(..., description="Current page number")
    pages: int = Field(..., description="Total number of pages")
    page_size: int = Field(..., description="Number of notifications per page")
    unread_count: int = Field(..., description="Number of unread notifications")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class UnreadCountResponse(BaseModel):
    """Response schema for unread notification count"""
    unread_count: int = Field(..., ge=0, description="Number of unread notifications")


class NotificationStatsResponse(BaseModel):
    """Response schema for notification statistics"""
    total_notifications: int
    unread_count: int
    read_count: int
    by_type: Dict[str, int] = Field(..., description="Count by notification type")
    by_priority: Dict[str, int] = Field(..., description="Count by priority level")
    urgent_count: int = Field(..., description="Count of high-priority notifications")


class SendNotificationResponse(BaseModel):
    """Response schema for sent notifications"""
    id: int
    message: str = "Notification sent successfully"
    notification: NotificationResponse

    class Config:
        from_attributes = True


class BulkActionResponse(BaseModel):
    """Response schema for bulk operations"""
    success: bool
    count: int = Field(..., description="Number of notifications affected")
    message: str


class NotificationPreferencesResponse(BaseModel):
    """Response schema for notification preferences (future feature)"""
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None    # "08:00"
    types_enabled: List[NotificationTypeEnum] = Field(
        default_factory=lambda: list(NotificationTypeEnum)
    )

    class Config:
        use_enum_values = True


# Error Response Schemas
class NotificationError(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class ValidationError(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    details: List[Dict[str, Any]]