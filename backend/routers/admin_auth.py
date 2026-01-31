from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database.config import get_db
from models.admin import Admin, AdminRole
from models.user import User
from models.token_blacklist import TokenBlacklist
from models.active_session import ActiveSession
from utils.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from auth.dependencies import get_current_active_user
from schemas.auth import LoginResponse, UserProfile, MessageResponse
from schemas.admin import AdminLogin, AdminProfile
from datetime import datetime, timedelta
import pyotp
import qrcode
from io import BytesIO
import base64
from schemas.auth import (
    MFASetupResponse, MFAEnable, MFAVerify, MFADisable
)
from config import settings


router = APIRouter(prefix="/admin/auth", tags=["Admin Authentication"])

@router.post("/login", response_model=LoginResponse)
async def admin_login(
    credentials: AdminLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Admin login - requires MFA"""
    
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    
    # Find admin
    admin = db.query(Admin).filter(Admin.email == credentials.email).first()
    
    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Admin accounts MUST have MFA enabled
    if not admin.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MFA setup required for admin accounts. Contact system administrator."
        )
    
    # Return temporary token for MFA verification
    temp_token = create_access_token(
        data={"sub": str(admin.id), "type": "mfa_required", "role": admin.role.value},
        expires_delta=timedelta(minutes=5)
    )
    
    return LoginResponse(
        access_token=temp_token,
        refresh_token="",
        token_type="bearer",
        expires_in=300,
        user_type="admin",
        requires_mfa=True,
        mfa_enabled=True,
        user_id=admin.id,
        email=admin.email,
        name=admin.full_name,
        role=admin.role.value
    )


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Initialize MFA setup (generate secret and QR code)"""
    
    # Generate TOTP secret
    secret = pyotp.random_base32()
    
    # Generate provisioning URI
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name="SentiLex AI Advocate"
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Generate backup codes
    backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
    
    # Store secret temporarily (don't enable until verified)
    current_user.mfa_secret = secret
    current_user.mfa_backup_codes = ",".join(backup_codes)
    db.commit()
    
    return MFASetupResponse(
        secret=secret,
        qr_code_url=f"data:image/png;base64,{qr_code_base64}",
        backup_codes=backup_codes
    )

@router.post("/mfa/enable", response_model=MessageResponse)
async def enable_mfa(
    mfa_data: MFAEnable,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enable MFA after verification"""
    
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not initialized. Call /mfa/setup first"
        )
    
    # Verify code
    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(mfa_data.verification_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Enable MFA
    current_user.mfa_enabled = True
    current_user.mfa_enabled_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="MFA enabled successfully")

@router.post("/mfa/verify", response_model=LoginResponse)
async def verify_mfa(
    mfa_data: MFAVerify,
    db: Session = Depends(get_db)
):
    """Verify MFA code during login"""
    
    # Decode temporary token
    payload = decode_token(mfa_data.temp_token)
    if not payload or payload.get("type") != "mfa_required":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid temporary token"
        )
    
    user_id = payload.get("sub")
    role = payload.get("role", "user")
    
    # Determine if admin or regular user
    if role in ["superadmin", "admin"]:
        from models.admin import Admin
        user = db.query(Admin).filter(Admin.id == int(user_id)).first()
    else:
        user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user or not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MFA not enabled"
        )
    

    totp = pyotp.TOTP(user.mfa_secret)
    is_valid = totp.verify(mfa_data.code)
    
    # If TOTP fails, check backup codes
    if not is_valid and user.mfa_backup_codes:
        backup_codes = user.mfa_backup_codes.split(",")
        if mfa_data.code in backup_codes:
            is_valid = True
            # Remove used backup code
            backup_codes.remove(mfa_data.code)
            user.mfa_backup_codes = ",".join(backup_codes)
            db.commit()
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    # Create full session tokens
    access_token = create_access_token({"sub": str(user.id), "role": role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Decode to get JTI
    refresh_payload = decode_token(refresh_token)
    
    # Store active session
    session = ActiveSession(
        user_id=user.id,
        jti=refresh_payload["jti"],
        user_type="admin" if role in ["admin", "superadmin"] else "user",
        ip_address=mfa_data.ip_address or "unknown",
        user_agent=mfa_data.user_agent or "unknown",
        expires_at=datetime.utcfromtimestamp(refresh_payload["exp"])
    )
    db.add(session)
    
    # Update last login
    user.last_login = datetime.utcnow()
    if isinstance(user, Admin):
        user.last_login_ip = mfa_data.ip_address or "unknown"
        user.last_login_user_agent = mfa_data.user_agent or "unknown"
    db.commit()
    
    # Determine user type
    if role in ["admin", "superadmin"]:
        user_type = "admin"
        name = user.full_name
    else:
        user_type = "user" if role == "user" else "lawyer"
        name = f"{user.first_name} {user.last_name}" if hasattr(user, 'first_name') else user.full_name if hasattr(user, 'full_name') else user.email
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_type=user_type,
        requires_mfa=False,
        mfa_enabled=True,
        user_id=user.id,
        email=user.email,
        name=name,
        role=role if role in ["admin", "superadmin"] else None
    )

@router.post("/mfa/disable", response_model=MessageResponse)
async def disable_mfa(
    password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disable MFA (requires password confirmation)"""
    
    if not verify_password(password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )
    
    # Admins cannot disable MFA
    if hasattr(current_user, 'role') and current_user.role in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin accounts cannot disable MFA"
        )
    
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    current_user.mfa_backup_codes = None
    db.commit()
    
    return MessageResponse(message="MFA disabled successfully")

@router.post("/mfa/regenerate-backup-codes", response_model=MFASetupResponse)
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Regenerate MFA backup codes"""
    
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled"
        )
    
    # Generate new backup codes
    backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
    current_user.mfa_backup_codes = ",".join(backup_codes)
    db.commit()
    
    return MFASetupResponse(
        secret=current_user.mfa_secret,
        qr_code_url="",
        backup_codes=backup_codes
    )