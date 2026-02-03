from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from database.config import get_db
from models.user import User
from models.login_attempt import LoginAttempt
from utils.auth import decode_token
from config import settings

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """
    Get the current authenticated user from the JWT token.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify the user is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def check_account_lockout(email: str, db: Session):
    """
    Check if the account is temporarily locked due to failed login attempts.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked. Try again after {user.locked_until}"
        )

def log_login_attempt(email, success, ip_address, user_agent, failure_reason, db):
    """
    Log a login attempt to the database.
    """
    # Find user_id if user exists
    user = db.query(User).filter(User.email == email).first()
    user_id = user.id if user else None
    
    attempt = LoginAttempt(
        email=email,
        user_id=user_id,
        user_type='user', # defaulting to user
        success=success,
        ip_address=ip_address,
        user_agent=user_agent,
        failure_reason=failure_reason
    )
    db.add(attempt)
    db.commit()

async def get_current_lawyer(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Get the current authenticated lawyer from the JWT token.
    """
    from models.lawyers import Lawyer
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Check if this is a lawyer token
    role = payload.get("role")
    if role != "lawyer":
        raise HTTPException(status_code=403, detail="Not authorized as a lawyer")
        
    lawyer_id: str = payload.get("sub")
    if lawyer_id is None:
        raise credentials_exception
        
    lawyer = db.query(Lawyer).filter(Lawyer.id == int(lawyer_id)).first()
    if lawyer is None:
        raise credentials_exception
        
    return lawyer

async def get_current_admin(current_user: User = Depends(get_current_user)):
    """
    Verify the current user is an admin.
    """
    if current_user.role != "admin" and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Not authorized as an admin")
    return current_user
