import bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional, Dict, Any
import secrets
import json
import hashlib
from config import settings
from sqlalchemy.orm import Session

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with SHA256 pre-hash
    Pre-hash with SHA256 to handle passwords > 72 bytes
    """
    # Pre-hash with SHA256 to handle any length password (avoids bcrypt 72-byte limit)
    prehash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # Bcrypt hash the SHA256 hex string
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(prehash.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    Pre-hash with SHA256 to match the hashing process
    """
    # Apply same SHA256 pre-hash as in hash_password
    prehash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return bcrypt.checkpw(prehash.encode('utf-8'), hashed_password.encode('utf-8'))

# Token management
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add unique JTI (JSON Token Identifier) for token revocation
    if "jti" not in to_encode:
        to_encode["jti"] = secrets.token_hex(16)
    
    # Only set type to "access" if not already set (allows for "mfa_required", etc.)
    if "type" not in to_encode:
        to_encode["type"] = "access"
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new refresh token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Add unique JTI (JSON Token Identifier)
    if "jti" not in to_encode:
        to_encode["jti"] = secrets.token_hex(16)
        
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT token and check if it's blacklisted"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Check if token is blacklisted (revoked after logout or password change)
        if db and "jti" in payload:
            from models.token_blacklist import TokenBlacklist
            blacklist_entry = db.query(TokenBlacklist).filter(
                TokenBlacklist.jti == payload["jti"]
            ).first()
            if blacklist_entry:
                # Token has been revoked (logged out, password changed, etc.)
                return None
        
        return payload
    except JWTError:
        return None

# Verification tokens
def generate_verification_token(email: str) -> str:
    """Generate a token for email verification (expires in 24 hours)"""
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "exp": expire, 
        "type": "email_verification",
        "email": email
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def generate_password_reset_token(email: str) -> str:
    """Generate a token for password reset (expires in 1 hour)"""
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {
        "exp": expire, 
        "type": "password_reset",
        "email": email
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# Password History Management
def check_password_history(user, new_password: str) -> bool:
    """Check if password was used in the last 5 password changes"""
    if not user.password_history:
        return True
    
    try:
        history = json.loads(user.password_history)
    except (json.JSONDecodeError, TypeError):
        return True
    
    # Check against last 5 passwords
    for old_hash in history[-5:]:
        if verify_password(new_password, old_hash):
            return False
    
    return True


def update_password_history(user, new_hash: str):
    """Add new password hash to history, keeping last 5"""
    try:
        history = json.loads(user.password_history or "[]")
    except (json.JSONDecodeError, TypeError):
        history = []
    
    # Add new hash and keep only last 5
    history.append(new_hash)
    user.password_history = json.dumps(history[-5:])
