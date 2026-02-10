# 🔔 Notification System Documentation

## Overview

This is a comprehensive, production-ready notification system designed for the SentiLex legal services platform. It supports Users, Lawyers, and Admins with a clean, scalable architecture.

## 🏗️ Architecture

### Clean Architecture Layers

```
Controller (FastAPI Router) 
    ↓
Service Interface (Abstract Base Class)
    ↓  
Concrete Service Implementation
    ↓
Database Layer (SQLAlchemy ORM)
```

### SOLID Principles Applied

1. **Single Responsibility**: Each service handles one recipient type
2. **Open/Closed**: Easy to extend with new notification channels
3. **Liskov Substitution**: All services implement the same interface
4. **Interface Segregation**: Clean, focused interface
5. **Dependency Inversion**: Depend on abstractions, not concretions

## 🗃️ Database Design

### Why Single Table?

✅ **Advantages:**
- **Consistency**: Unified structure for all notification types
- **Performance**: Single table queries are faster
- **Maintainability**: One model to update and test
- **Analytics**: Easy cross-user-type reporting
- **Extensibility**: Add new recipient types without schema changes

❌ **Multiple Tables Would Have:**
- Code duplication across models
- Complex joins for admin dashboards  
- Inconsistent behavior across user types
- More difficult migrations

### Table Schema

```sql
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    recipient_id INT NOT NULL,                    -- References user/lawyer/admin ID
    recipient_type ENUM('USER','LAWYER','ADMIN'), -- Recipient type
    title VARCHAR(200) NULL,                      -- Optional heading
    message TEXT NOT NULL,                        -- Main content
    type ENUM('SYSTEM','CASE_UPDATE',...),        -- Notification category
    is_read BOOLEAN DEFAULT FALSE,                -- Read status
    read_at TIMESTAMP NULL,                       -- When read
    is_deleted BOOLEAN DEFAULT FALSE,             -- Soft delete
    created_at TIMESTAMP DEFAULT NOW(),           -- Creation time
    priority INT DEFAULT 1,                       -- 1=low, 2=med, 3=high
    action_url VARCHAR(500) NULL,                 -- Deep link
    metadata_json TEXT NULL,                      -- Extensibility
    expires_at TIMESTAMP NULL,                    -- Expiration
    -- Optimized indexes for performance...
);
```

## 🚀 Usage Examples

### 1. Basic Service Usage

```python
from services.notification_service import create_notification_service
from models.notification import RecipientTypeEnum, NotificationTypeEnum

# Create service for lawyers
service = create_notification_service(RecipientTypeEnum.LAWYER, db_session)

# Send basic notification
notification = service.send(
    recipient_id=123,
    message="Your verification has been approved!",
    title="🎉 Verification Complete",
    notification_type=NotificationTypeEnum.VERIFICATION,
    priority=3
)

# Get unread notifications
unread = service.get_unread(123, limit=10)

# Mark as read
service.mark_as_read(notification.id, 123)
```

### 2. Lawyer Verification Example

```python
# In your verification workflow
from services.notification_service import LawyerNotificationService

lawyer_service = LawyerNotificationService(db_session)

# Send verification update
notification = lawyer_service.send_verification_update(
    lawyer_id=456,
    status="approved",
    next_step="You can now accept cases"
)
```

### 3. Case Update Example

```python
# In your case management system
from services.notification_service import UserNotificationService

user_service = UserNotificationService(db_session)

# Notify user of case progress
notification = user_service.send_case_update(
    user_id=789,
    case_title="Personal Injury Claim",
    status="Under Review",
    case_id=101
)
```

## 📡 REST API Examples

### Get My Notifications

```bash
GET /api/notifications/my?page=1&page_size=20&type=CASE_UPDATE

Response:
{
    "notifications": [...],
    "total": 45,
    "page": 1,
    "pages": 3,
    "page_size": 20,
    "unread_count": 12
}
```

### Send Notification (Admin Only)

```bash
POST /api/notifications/send
{
    "recipient_id": 123,
    "recipient_type": "LAWYER",
    "title": "Important Update",
    "message": "New legal regulations effective immediately.",
    "type": "LEGAL_UPDATE",
    "priority": 3,
    "action_url": "/legal-updates/2024-001"
}

Response:
{
    "id": 1001,
    "message": "Notification sent successfully",
    "notification": { ... }
}
```

### Mark Notifications as Read

```bash
POST /api/notifications/my/mark-read
{
    "notification_ids": [1001, 1002, 1003]
}

Response:
{
    "success": true,
    "count": 3,
    "message": "Marked 3 notifications as read"
}
```

### Get Unread Count

```bash
GET /api/notifications/my/count

Response:
{
    "unread_count": 7
}
```

## 🔌 Integration Points

### 1. Lawyer Verification Integration

```python
# In your existing verification router
from services.notification_service import LawyerNotificationService

@router.post("/verify-step-4")
def submit_step_4(
    data: VerificationStep4,
    db: Session = Depends(get_db),
    current_lawyer: Lawyer = Depends(get_current_lawyer)
):
    # Your existing verification logic...
    lawyer.verification_status = VerificationStatusEnum.pending
    db.commit()
    
    # Add notification
    notification_service = LawyerNotificationService(db)
    notification_service.send_verification_update(
        lawyer_id=current_lawyer.id,
        status="submitted",
        next_step="Your documents are under review. You'll be notified within 48 hours."
    )
    
    return {"message": "Verification submitted successfully"}
```

### 2. Case Status Integration

```python
# In your case management system
def update_case_status(case_id: int, new_status: str, db: Session):
    case = db.query(Case).filter(Case.id == case_id).first()
    case.status = new_status
    db.commit()
    
    # Notify client
    user_service = UserNotificationService(db)
    user_service.send_case_update(
        user_id=case.client_id,
        case_title=case.title,
        status=new_status,
        case_id=case_id
    )
```

### 3. WebSocket Integration (Future)

```python
# Real-time notifications via WebSocket
from fastapi import WebSocket

@app.websocket("/ws/notifications/{user_id}")
async def notification_websocket(websocket: WebSocket, user_id: int):
    await websocket.accept()
    
    # Subscribe to user's notification updates
    # Broadcast new notifications in real-time
    while True:
        # Check for new notifications
        new_notifications = check_new_notifications(user_id)
        if new_notifications:
            await websocket.send_json({
                "type": "new_notification",
                "data": new_notifications
            })
        await asyncio.sleep(5)  # Poll every 5 seconds
```

## 🎯 Advanced Features

### 1. Event-Driven Notifications

```python
# Using background tasks
from fastapi import BackgroundTasks

def send_notification_async(recipient_id: int, message: str):
    """Send notification in background"""
    # Implementation here
    pass

@router.post("/some-action")
def perform_action(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Perform main action
    
    # Queue notification for background sending
    background_tasks.add_task(
        send_notification_async,
        recipient_id=123,
        message="Action completed successfully"
    )
```

### 2. Email/SMS Integration

```python
class LawyerNotificationService(NotificationService):
    def _post_send_hook(self, notification: Notification) -> None:
        """Send email for high-priority notifications"""
        if notification.priority >= 3:
            send_email(
                to_email=get_lawyer_email(notification.recipient_id),
                subject=notification.title,
                body=notification.message
            )
```

### 3. Notification Preferences

```python
# Future: User preferences for notification channels
class NotificationPreferences(Base):
    __tablename__ = "notification_preferences"
    
    user_id = Column(Integer, primary_key=True)
    user_type = Column(Enum(RecipientTypeEnum))
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(String(5))  # "22:00"
    quiet_hours_end = Column(String(5))    # "08:00"
```

## 🔒 Security Considerations

1. **Authorization**: Users can only access their own notifications
2. **Validation**: All inputs are validated via Pydantic schemas
3. **SQL Injection**: Using SQLAlchemy ORM prevents injection
4. **Rate Limiting**: Consider adding rate limits for notification sending
5. **Audit Trail**: All notification actions are logged

## 📊 Performance Optimizations

1. **Database Indexes**: Optimized for common query patterns
2. **Pagination**: All list endpoints support pagination
3. **Soft Delete**: No hard deletes for audit trails
4. **Background Processing**: Heavy operations can be queued
5. **Caching**: Consider Redis for notification counts

## 🚀 Deployment Checklist

1. **Run Migration**: Execute the table creation script
2. **Environment Setup**: Configure database connection
3. **Register Router**: Add to main FastAPI app
4. **Test Endpoints**: Verify all API endpoints work
5. **Monitor Performance**: Set up logging and metrics

## 🔮 Future Enhancements

1. **Real-time Updates**: WebSocket support for instant notifications
2. **Push Notifications**: Mobile app push notifications
3. **Email Templates**: Rich HTML email notifications
4. **SMS Integration**: Twilio integration for urgent notifications
5. **Notification Analytics**: Dashboard for notification metrics
6. **A/B Testing**: Test different notification strategies
7. **Machine Learning**: Personalized notification timing
8. **Bulk Operations**: Mass notification capabilities

This notification system provides a solid foundation that can scale with your platform's growth while maintaining clean architecture principles!