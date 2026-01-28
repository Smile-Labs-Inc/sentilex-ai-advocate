"""
Authentication Dependencies for Lawyer Verification System

TODO: Implement JWT-based authentication for production use.
Current implementation uses mock data for development.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.config import get_db
from models.lawyers import Lawyer

security = HTTPBearer()


def get_current_lawyer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Lawyer:
    """
    Retrieve the currently authenticated lawyer.
    
    TODO: Implement JWT token validation:
    1. Decode JWT token from credentials.credentials
    2. Verify signature and expiration
    3. Extract lawyer_id from token payload
    4. Query database for lawyer
    5. Return lawyer object
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        Authenticated Lawyer object
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    # MOCK IMPLEMENTATION - Replace with actual JWT validation
    # For now, just get the first lawyer for testing
    lawyer = db.query(Lawyer).first()
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. No lawyers in database.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return lawyer


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Retrieve the currently authenticated admin user.
    
    TODO: Implement admin JWT token validation:
    1. Decode JWT token
    2. Verify admin role in token claims
    3. Query admin user from database
    4. Return admin object
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        
    Returns:
        Authenticated Admin object (dict for now)
        
    Raises:
        HTTPException: 401 if not authenticated, 403 if not admin
    """
    # MOCK IMPLEMENTATION - Replace with actual admin auth
    # For testing, return a mock admin object
    return {
        "id": 1,
        "role": "admin",
        "email": "admin@sentilex.lk"
    }


def get_optional_lawyer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Lawyer | None:
    """
    Retrieve the currently authenticated lawyer, or None if not authenticated.
    Useful for endpoints that work both authenticated and unauthenticated.
    
    Args:
        credentials: Bearer token (optional)
        db: Database session
        
    Returns:
        Lawyer object or None
    """
    try:
        return get_current_lawyer(credentials, db)
    except HTTPException:
        return None
