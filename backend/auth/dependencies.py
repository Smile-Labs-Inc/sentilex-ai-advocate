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
    Validates token signature and checks if token is blacklisted.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token, db)  # Pass db for blacklist check
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

async def get_current_lawyer(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)):
    """
    Get the current authenticated lawyer from the JWT token.
    Returns None if not a lawyer token or not authenticated.
    """
    from models.lawyers import Lawyer
    
    if not credentials:
        return None
        
    token = credentials.credentials
    
    payload = decode_token(token, db)
    if payload is None:
        return None
    
    # Check if this is a lawyer token
    role = payload.get("role")
    if role != "lawyer":
        return None
        
    lawyer_id: str = payload.get("sub")
    if lawyer_id is None:
        return None
        
    lawyer = db.query(Lawyer).filter(Lawyer.id == int(lawyer_id)).first()
    return lawyer

async def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)) -> Optional[User]:
    """
    Get the current authenticated user from the JWT token.
    Returns None if not authenticated.
    """
    if not credentials:
        return None
        
    token = credentials.credentials
    payload = decode_token(token, db)
    if payload is None:
        return None
        
    user_id: str = payload.get("sub")
    if user_id is None:
        return None
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user

async def get_current_admin(current_user: Optional[User] = Depends(get_optional_current_user)) -> Optional[User]:
    """
    Verify the current user is an admin.
    Returns None if not an admin or not authenticated.
    """
    if current_user and (current_user.role == "admin" or current_user.role == "superadmin"):
        return current_user
    return None
