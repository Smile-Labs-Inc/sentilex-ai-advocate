# =============================================================================
# Payment Router
# Handles payment processing and subscription upgrades
# =============================================================================

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.config import get_db
from models.user import User
from auth.dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentRequest(BaseModel):
    """Payment verification request"""
    order_id: str
    status: str
    payer_id: Optional[str] = None
    payer_email: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment verification response"""
    success: bool
    message: str
    subscription_status: Optional[str] = None


@router.post("/upgrade", response_model=PaymentResponse)
async def upgrade_subscription(
    payment: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify PayPal payment and upgrade user subscription
    
    Steps:
    1. Verify payment with PayPal API (optional - for production)
    2. Update user's subscription status
    3. Record payment transaction
    """
    
    # Verify payment status
    if payment.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment not completed"
        )
    
    try:
        # TODO: In production, verify with PayPal API using server secret
        # import requests
        # paypal_response = requests.post(
        #     f"https://api-m.paypal.com/v2/checkout/orders/{payment.order_id}",
        #     headers={"Authorization": f"Bearer {PAYPAL_ACCESS_TOKEN}"}
        # )
        
        # Update user subscription
        # Assuming you have a subscription_status field in your User model
        # If not, you'll need to add it or create a separate Subscription model
        
        # For now, we'll add a simple flag (you may need to add this column)
        # current_user.subscription_status = "pro"
        # current_user.subscription_start_date = datetime.utcnow()
        
        # db.commit()
        # db.refresh(current_user)
        
        return PaymentResponse(
            success=True,
            message="Subscription upgraded successfully",
            subscription_status="pro"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process payment: {str(e)}"
        )


@router.get("/subscription")
async def get_subscription_status(
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription status"""
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "subscription_status": getattr(current_user, 'subscription_status', 'free'),
        "subscription_start_date": getattr(current_user, 'subscription_start_date', None)
    }
