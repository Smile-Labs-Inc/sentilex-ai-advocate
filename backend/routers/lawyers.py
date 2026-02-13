from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from database.config import get_db
from models.lawyers import Lawyer, VerificationStatusEnum
from models.active_session import ActiveSession
from models.token_blacklist import TokenBlacklist
from schemas.lawyers import (
    LawyerResponse, LawyerRegister, LawyerLogin,
    LawyerProfileResponse, PasswordChange, PasswordResetRequest, PasswordReset,
    EmailVerification, SessionResponse
)
from schemas.auth import LoginResponse, MessageResponse, TokenResponse
from utils.email import send_verification_email, send_password_reset_email, send_password_changed_email
from utils.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, generate_verification_token, generate_password_reset_token,
    check_password_history, update_password_history
)
from auth.dependencies import get_current_user, get_current_lawyer, log_login_attempt, check_account_lockout
from datetime import datetime, timedelta
import config


router = APIRouter(
    prefix="/lawyers",
    tags=["Lawyers"]
)

@router.get("/", response_model=list[LawyerResponse])
def get_lawyers(
    district: str | None = None,
    specialty: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Lawyer)

    if district:
        query = query.filter(Lawyer.district == district)

    if specialty:
        query = query.filter(Lawyer.specialties.ilike(f"%{specialty}%"))

    return query.all()

@router.post("/register", response_model=LawyerResponse)
async def register_lawyer(
    lawyer_data: LawyerRegister,
    db: Session = Depends(get_db)
):
    from models.lawyers import Lawyer, VerificationStatusEnum
    
    # Check existing email
    existing = db.query(Lawyer).filter(Lawyer.email == lawyer_data.email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    
    # Create lawyer account
    lawyer = Lawyer(
        name=lawyer_data.name,
        email=lawyer_data.email,
        password_hash=hash_password(lawyer_data.password.get_secret_value()),
        phone=lawyer_data.phone,
        district=lawyer_data.district,
        specialties=lawyer_data.specialties,
        experience_years=lawyer_data.experience_years,
        verification_status=VerificationStatusEnum.not_started,
        verification_step=1,
        is_active=True,
        is_email_verified=False
    )
    
    db.add(lawyer)
    db.commit()
    db.refresh(lawyer)
    
    # Send verification email
    verification_token = generate_verification_token(lawyer.email)
    send_verification_email(lawyer.email, verification_token, lawyer.name)
    
    return lawyer

@router.post("/login", response_model=LoginResponse)
async def login_lawyer(
    credentials: LawyerLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Lawyer login with verification status check"""
    
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Check account lockout
    check_account_lockout(credentials.email, db)
    
    # Find lawyer
    lawyer = db.query(Lawyer).filter(Lawyer.email == credentials.email).first()
    
    if not lawyer:
        log_login_attempt(credentials.email, False, ip_address, user_agent, "lawyer_not_found", db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password.get_secret_value(), lawyer.password_hash):
        log_login_attempt(credentials.email, False, ip_address, user_agent, "invalid_password", db)
        
        # Increment failed attempts
        lawyer.failed_login_attempts = (lawyer.failed_login_attempts or 0) + 1
        
        # Lock account after 5 failed attempts
        if lawyer.failed_login_attempts >= 5:
            lawyer.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if account is active
    if not lawyer.is_active:
        log_login_attempt(credentials.email, False, ip_address, user_agent, "account_inactive", db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Check email verification
    if not lawyer.is_email_verified:
        log_login_attempt(credentials.email, False, ip_address, user_agent, "email_not_verified", db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )
    
    # Check lawyer verification status
    if lawyer.verification_status == VerificationStatusEnum.rejected:
        log_login_attempt(credentials.email, False, ip_address, user_agent, "verification_rejected", db)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your lawyer verification was rejected. Please contact support."
        )
    
    # Allow login but inform about pending verification
    warning_message = None
    if lawyer.verification_status != VerificationStatusEnum.approved:
        warning_message = f"Your verification is {lawyer.verification_status.value}. Some features may be limited."
    
    # Check if MFA is enabled
    if lawyer.mfa_enabled:
        # Return temporary token for MFA verification
        temp_token = create_access_token(
            data={"sub": str(lawyer.id), "type": "mfa_required", "role": "lawyer"},
            expires_delta=timedelta(minutes=5)
        )
        
        log_login_attempt(credentials.email, True, ip_address, user_agent, "mfa_required", db)
        
        return LoginResponse(
            access_token=temp_token,
            refresh_token="",
            token_type="bearer",
            expires_in=300,
            user_type="lawyer",
            requires_mfa=True,
            mfa_enabled=True,
            user_id=lawyer.id,
            email=lawyer.email,
            name=lawyer.name,
            role=None
        )
    
    # Create tokens (only if MFA is not enabled)
    access_token = create_access_token(data={"sub": str(lawyer.id), "role": "lawyer"})
    refresh_token = create_refresh_token(data={"sub": str(lawyer.id)})
    
    # Decode to get JTI
    refresh_payload = decode_token(refresh_token)
    
    # Store active session
    session = ActiveSession(
        user_id=lawyer.id,
        user_type="lawyer",
        jti=refresh_payload["jti"],
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.utcfromtimestamp(refresh_payload["exp"])
    )
    db.add(session)
    
    # Update lawyer
    lawyer.last_login = datetime.utcnow()
    lawyer.failed_login_attempts = 0
    lawyer.locked_until = None
    
    db.commit()
    
    # Log successful login
    log_login_attempt(credentials.email, True, ip_address, user_agent, None, db)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_type="lawyer",
        requires_mfa=False,
        mfa_enabled=lawyer.mfa_enabled,
        user_id=lawyer.id,
        email=lawyer.email,
        name=lawyer.name,
        role=None
    )


@router.get("/me", response_model=LawyerProfileResponse)
async def get_lawyer_profile(
    current_lawyer: Lawyer = Depends(get_current_lawyer),
    db: Session = Depends(get_db)
):
    """Get current lawyer profile"""
    
    # Count active sessions
    active_sessions_count = db.query(ActiveSession).filter(
        ActiveSession.user_id == current_lawyer.id,
        ActiveSession.user_type == "lawyer",
        ActiveSession.expires_at > datetime.utcnow()
    ).count()
    
    # Create response with active sessions count
    lawyer_data = LawyerProfileResponse.from_orm(current_lawyer)
    lawyer_data.active_sessions = active_sessions_count
    
    return lawyer_data


@router.put("/me", response_model=LawyerProfileResponse)
async def update_lawyer_profile(
    updates: dict,
    current_lawyer: Lawyer = Depends(get_current_lawyer),
    db: Session = Depends(get_db)
):
    """Update current lawyer profile"""
    
    # Only allow updating specific fields
    allowed_fields = ["name", "phone", "district", "specialties", "availability", "experience_years"]
    
    for field, value in updates.items():
        if field in allowed_fields and hasattr(current_lawyer, field):
            setattr(current_lawyer, field, value)
    
    db.commit()
    db.refresh(current_lawyer)
    
    return LawyerProfileResponse.from_orm(current_lawyer)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_lawyer_email(
    verification: EmailVerification,
    db: Session = Depends(get_db)
):
    """Verify lawyer email"""
    
    payload = decode_token(verification.token)
    
    if payload is None or payload.get("type") != "email_verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    email = payload.get("email")
    lawyer = db.query(Lawyer).filter(Lawyer.email == email).first()
    
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )
    
    lawyer.is_email_verified = True
    db.commit()
    
    return MessageResponse(message="Email verified successfully. You can now proceed with lawyer verification.")


@router.post("/change-password", response_model=MessageResponse)
async def change_lawyer_password(
    password_data: PasswordChange,
    request: Request,
    current_lawyer: Lawyer = Depends(get_current_lawyer),
    db: Session = Depends(get_db)
):
    """Change lawyer password"""
    
    current_pass = password_data.current_password.get_secret_value()
    new_pass = password_data.new_password.get_secret_value()
    
    # Verify current password
    if not verify_password(current_pass, current_lawyer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new password is same as current
    if verify_password(new_pass, current_lawyer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Check password history
    if not check_password_history(current_lawyer, new_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reuse any of your last 5 passwords"
        )
    
    # Update password history
    update_password_history(current_lawyer, current_lawyer.password_hash)
    
    # Update password
    current_lawyer.password_hash = hash_password(new_pass)
    current_lawyer.password_changed_at = datetime.utcnow()
    db.commit()
    
    # Send notification email
    ip_address = request.client.host
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    send_password_changed_email(current_lawyer.email, current_lawyer.name, ip_address, timestamp)
    
    return MessageResponse(message="Password changed successfully")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_lawyer_password(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset for lawyer"""
    
    lawyer = db.query(Lawyer).filter(Lawyer.email == reset_data.email).first()
    
    # Always return success to prevent email enumeration
    if lawyer and lawyer.is_active:
        reset_token = generate_password_reset_token(lawyer.email)
        send_password_reset_email(lawyer.email, reset_token, lawyer.name)
    
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_lawyer_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Reset lawyer password with token"""
    
    payload = decode_token(reset_data.token)
    
    if payload is None or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    email = payload.get("email")
    lawyer = db.query(Lawyer).filter(Lawyer.email == email).first()
    
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )
    
    new_pass = reset_data.new_password.get_secret_value()
    
    # Check password history
    if not check_password_history(lawyer, new_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reuse any of your last 5 passwords"
        )
    
    # Update password history
    update_password_history(lawyer, lawyer.password_hash)
    
    # Update password
    lawyer.password_hash = hash_password(new_pass)
    lawyer.failed_login_attempts = 0
    lawyer.locked_until = None
    lawyer.password_changed_at = datetime.utcnow()
    db.commit()
    
    # Send confirmation email
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    send_password_changed_email(lawyer.email, lawyer.name, "Password Reset", timestamp)
    
    return MessageResponse(message="Password reset successfully")


@router.get("/sessions", response_model=list[SessionResponse])
async def get_lawyer_sessions(
    current_lawyer: Lawyer = Depends(get_current_lawyer),
    db: Session = Depends(get_db)
):
    """Get all active sessions for current lawyer"""
    
    sessions = db.query(ActiveSession).filter(
        ActiveSession.user_id == current_lawyer.id,
        ActiveSession.user_type == "lawyer",
        ActiveSession.expires_at > datetime.utcnow()
    ).all()
    
    return [SessionResponse.from_orm(s) for s in sessions]


@router.delete("/sessions/{session_id}", response_model=MessageResponse)
async def revoke_lawyer_session(
    session_id: int,
    current_lawyer: Lawyer = Depends(get_current_lawyer),
    db: Session = Depends(get_db)
):
    """Revoke a specific session"""
    
    session = db.query(ActiveSession).filter(
        ActiveSession.id == session_id,
        ActiveSession.user_id == current_lawyer.id,
        ActiveSession.user_type == "lawyer"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Blacklist refresh token
    blacklist_entry = TokenBlacklist(
        jti=session.jti,
        token_type="refresh",
        user_id=current_lawyer.id,
        user_type="lawyer",
        reason="session_revoked",
        expires_at=session.expires_at
    )
    db.add(blacklist_entry)
    db.delete(session)
    db.commit()
    
    return MessageResponse(message="Session revoked successfully")