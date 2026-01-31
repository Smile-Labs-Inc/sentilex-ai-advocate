from fastapi import APIRouter, Depends, HTTPException, status,Request
from sqlalchemy.orm import Session
from database.config import get_db
from models.user import User
from models.token_blacklist import TokenBlacklist 
from models.active_session import ActiveSession

from utils.auth import hash_password, verify_password, create_access_token
from datetime import datetime,timedelta
from typing import Optional


from schemas.auth import (
    UserRegister, UserLogin, TokenResponse, TokenRefresh,
    PasswordReset, PasswordResetConfirm, PasswordChange,
    EmailVerification, UserProfile, LoginResponse,
    RegistrationResponse, LogoutResponse, MessageResponse,
    ActiveSessionsResponse, SessionInfo
)
from utils.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_verification_token, generate_password_reset_token
)

from utils.email import (
    send_verification_email,
    send_password_reset_email,
    send_password_changed_email,
    send_welcome_email
)

from auth.dependencies import (
    get_current_user, get_current_active_user,
    check_account_lockout, log_login_attempt
)
import config


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        preferred_language=user_data.preferred_language,
        district=user_data.district,
        role="user",
        is_active=True,
        email_verified=False  # Require email verification
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    #Send verification email
    verification_token = generate_verification_token(new_user.email)
    user_name = f"{new_user.first_name} {new_user.last_name}"
    send_verification_email(new_user.email, verification_token, user_name)

    return RegistrationResponse(
        message="Registration successful. Please verify your email.",
        user=UserProfile.from_orm(new_user),
        verification_sent=True
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    
    # Get client info
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    
    # Check account lockout
    check_account_lockout(credentials.email, db)
    
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        log_login_attempt(credentials.email, False, ip_address, user_agent, "user_not_found", db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        log_login_attempt(credentials.email, False, ip_address, user_agent, "invalid_password", db)
        
        # Increment failed attempts
        user.failed_login_attempts += 1
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if account is active
    if not user.is_active:
        log_login_attempt(credentials.email, False, ip_address, user_agent, "account_inactive", db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Decode to get JTI
    refresh_payload = decode_token(refresh_token)
    
    # Store active session
    session = ActiveSession(
        user_id=user.id,
        refresh_token_jti=refresh_payload["jti"],
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.utcfromtimestamp(refresh_payload["exp"])
    )
    db.add(session)
    
    # Update user
    user.last_login_at = datetime.utcnow()
    user.failed_login_attempts = 0
    
    db.commit()
    
    # Log successful login
    log_login_attempt(credentials.email, True, ip_address, user_agent, None, db)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserProfile.from_orm(user),
        requires_mfa=user.mfa_enabled,
        mfa_enabled=user.mfa_enabled
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    # Decode refresh token
    payload = decode_token(token_data.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if token is blacklisted
    jti = payload.get("jti")
    is_blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
    
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )
    
    # Verify session exists
    session = db.query(ActiveSession).filter(
        ActiveSession.refresh_token_jti == jti
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    # Get user
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    
    # Update session last activity
    session.last_activity = datetime.utcnow()
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=token_data.refresh_token,
        token_type="bearer",
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout current user (revoke all refresh tokens)"""
    
    # Get all active sessions for user
    sessions = db.query(ActiveSession).filter(
        ActiveSession.user_id == current_user.id
    ).all()
    
    # Blacklist all refresh tokens
    for session in sessions:
        blacklist_entry = TokenBlacklist(
            jti=session.refresh_token_jti,
            token_type="refresh",
            user_id=current_user.id,
            expires_at=session.expires_at
        )
        db.add(blacklist_entry)
        db.delete(session)
    
    db.commit()
    
    return LogoutResponse(message="Successfully logged out")

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return UserProfile.from_orm(current_user)

@router.get("/sessions", response_model=ActiveSessionsResponse)
async def get_active_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all active sessions for current user"""
    sessions = db.query(ActiveSession).filter(
        ActiveSession.user_id == current_user.id
    ).all()
    
    return ActiveSessionsResponse(
        sessions=[SessionInfo.from_orm(s) for s in sessions],
        total=len(sessions)
    )

@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session"""
    session = db.query(ActiveSession).filter(
        ActiveSession.id == session_id,
        ActiveSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Blacklist refresh token
    blacklist_entry = TokenBlacklist(
        jti=session.refresh_token_jti,
        token_type="refresh",
        user_id=current_user.id,
        expires_at=session.expires_at
    )
    db.add(blacklist_entry)
    db.delete(session)
    db.commit()
    
    return MessageResponse(message="Session revoked successfully")

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification: EmailVerification,
    db: Session = Depends(get_db)
):
    """Verify user email"""
    
    payload = decode_token(verification.token)
    
    if payload is None or payload.get("type") != "email_verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    email = payload.get("email")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.email_verified = True
    db.commit()
    user_name = f"{user.first_name} {user.last_name}"
    send_welcome_email(user.email, user_name)
    
    return MessageResponse(message="Email verified successfully")

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = hash_password(password_data.new_password)
    db.commit()
    
    #Send password change notification email
    user_name = f"{current_user.first_name} {current_user.last_name}"
    ip_address = request.client.host
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    send_password_changed_email(current_user.email, user_name, ip_address, timestamp)
    return MessageResponse(message="Password changed successfully")

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    
    user = db.query(User).filter(User.email == reset_data.email).first()
    
    # Always return success to prevent email enumeration
    # Send password reset email
    if user and user.is_active:
        #Send password reset email
        reset_token = generate_password_reset_token(user.email)
        user_name = f"{user.first_name} {user.last_name}"
        send_password_reset_email(user.email, reset_token, user_name)
    
    
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    
    payload = decode_token(reset_data.token)
    
    if payload is None or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    email = payload.get("email")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = hash_password(reset_data.new_password)
    user.failed_login_attempts = 0
    db.commit()
    
    #Send password reset confirmation email
    user_name = f"{user.first_name} {user.last_name}"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    send_password_changed_email(user.email, user_name, "Password Reset", timestamp)
    
    return MessageResponse(message="Password reset successfully")