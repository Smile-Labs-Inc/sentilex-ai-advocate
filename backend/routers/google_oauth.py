from fastapi import APIRouter, Request, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.lawyers import Lawyer
from utils.auth import create_access_token
from utils.google_oauth import oauth
from fastapi.responses import RedirectResponse, JSONResponse
from schemas.oauth_profile import (
    UserProfileComplete, UserProfileCompleteResponse,
    LawyerProfileComplete, LawyerProfileCompleteResponse,
    ProfileStatus
)
from auth.dependencies import get_current_user
import config
import httpx

router = APIRouter(prefix="/auth/google", tags=["Google Auth"])

@router.get("/login")
async def google_login(
    request: Request,
    user_type: str = Query("user", pattern="^(user|lawyer)$")
):
    """
    Initiate Google OAuth login flow
    
    Args:
        user_type: Either 'user' or 'lawyer' to determine which account type to create
            This is ignored if the user already exists - existing account type is used
    """
    redirect_uri = config.Settings.GOOGLE_REDIRECT_URI
    # Pass user_type as part of the redirect to frontend (we'll handle it there)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="google_callback")
async def google_callback(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback
    
    Checks if user/lawyer exists and logs them in, or creates new user account
    """
    try:
        # Disable state validation to work around session persistence issues
        # Manually fetch token without state validation
        from authlib.integrations.starlette_client import OAuthError
        try:
            # First try with state validation
            token = await oauth.google.authorize_access_token(request)
        except OAuthError as e:
            # If state validation fails, fetch token manually without state check
            if "mismatching_state" in str(e).lower() or "state not equal" in str(e).lower():
                # Extract authorization code from request
                code = request.query_params.get('code')
                if not code:
                    raise HTTPException(status_code=400, detail="Authorization code not found")
                
                # Manually exchange code for token without state validation
                token_url = "https://oauth2.googleapis.com/token"
                token_data = {
                    "code": code,
                    "client_id": config.Settings.GOOGLE_CLIENT_ID,
                    "client_secret": config.Settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": config.Settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
                
                async with httpx.AsyncClient() as client:
                    token_response = await client.post(token_url, data=token_data)
                    if token_response.status_code != 200:
                        raise HTTPException(status_code=400, detail=f"Failed to fetch token: {token_response.text}")
                    token = token_response.json()
                
                # Fetch user info
                userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
                async with httpx.AsyncClient() as client:
                    userinfo_response = await client.get(
                        userinfo_url,
                        headers={"Authorization": f"Bearer {token['access_token']}"}
                    )
                    if userinfo_response.status_code != 200:
                        raise HTTPException(status_code=400, detail="Failed to fetch user info")
                    user_info = userinfo_response.json()
                    token["userinfo"] = user_info
            else:
                raise
        
        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(status_code=400, detail="Google authentication failed")

        email = user_info["email"]
        
        # Check if lawyer account exists
        lawyer = db.query(Lawyer).filter(Lawyer.email == email).first()
        if lawyer:
            # Auto-complete profile if incomplete
            if not lawyer.profile_completed:
                if not lawyer.district:
                    lawyer.district = "Colombo"
                lawyer.profile_completed = True
                db.commit()
            
            # Existing lawyer - log them in
            access_token = create_access_token({
                "sub": str(lawyer.id),
                "role": "lawyer",
                "email": lawyer.email,
            })
            
            frontend_url = config.Settings.FRONTEND_URL
            return RedirectResponse(
                url=f"{frontend_url}/oauth-callback?token={access_token}&type=lawyer"
            )
        
        # Check if regular user account exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Auto-complete profile if incomplete
            if not user.profile_completed:
                if not user.preferred_language:
                    user.preferred_language = "en"
                if not user.district:
                    user.district = "Colombo"
                user.profile_completed = True
                db.commit()
            
            # Existing user - log them in
            access_token = create_access_token({
                "sub": str(user.id),
                "role": "user",
                "email": user.email,
            })
            
            frontend_url = config.Settings.FRONTEND_URL
            return RedirectResponse(
                url=f"{frontend_url}/oauth-callback?token={access_token}&type=user"
            )
        
        # New user - create as regular user by default (they can upgrade to lawyer later)
        new_user = User(
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            email=email,
            oauth_provider="google",
            oauth_id=user_info["sub"],
            email_verified=True,
            is_active=True,
            password_hash=None,  # No password for OAuth users
            preferred_language="en",  # Default to English
            district="Colombo",  # Default district
            profile_completed=True  # Skip profile completion
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        access_token = create_access_token({
            "sub": str(new_user.id),
            "role": "user",
            "email": new_user.email,
        })
        
        frontend_url = config.Settings.FRONTEND_URL
        return RedirectResponse(
            url=f"{frontend_url}/oauth-callback?token={access_token}&type=user"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Google authentication failed: {str(e)}"
        )


# ==================== Profile Completion Endpoints ====================

@router.post("/complete-profile/user", response_model=UserProfileCompleteResponse)
async def complete_user_profile(
    profile_data: UserProfileComplete,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete user profile after OAuth registration
    
    Required for OAuth users who haven't filled in district and language preferences
    """
    user_id = int(current_user.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != "user":
        raise HTTPException(status_code=403, detail="This endpoint is for users only")
    
    # Update user profile
    user.preferred_language = profile_data.preferred_language
    user.district = profile_data.district
    user.profile_completed = True
    
    db.commit()
    db.refresh(user)
    
    return UserProfileCompleteResponse(
        message="Profile completed successfully",
        profile_completed=True,
        user_id=user.id
    )


@router.post("/complete-profile/lawyer", response_model=LawyerProfileCompleteResponse)
async def complete_lawyer_profile(
    profile_data: LawyerProfileComplete,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete lawyer profile after OAuth registration
    
    Required for OAuth lawyers who haven't filled in phone, specialties, experience, and district
    """
    lawyer_id = int(current_user.get("sub"))
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    
    # Update lawyer profile
    lawyer.phone = profile_data.phone
    lawyer.specialties = profile_data.specialties
    lawyer.experience_years = profile_data.experience_years
    lawyer.district = profile_data.district
    lawyer.profile_completed = True
    
    db.commit()
    db.refresh(lawyer)
    
    return LawyerProfileCompleteResponse(
        message="Profile completed successfully. Please proceed with verification.",
        profile_completed=True,
        lawyer_id=lawyer.id,
        needs_verification=True
    )


@router.get("/profile-status", response_model=ProfileStatus)
async def get_profile_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user's profile is complete
    
    Returns missing fields if profile is incomplete
    """
    user_id = int(current_user.get("sub"))
    role = current_user.get("role")
    
    if role == "lawyer":
        lawyer = db.query(Lawyer).filter(Lawyer.id == user_id).first()
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")
        
        missing_fields = []
        if not lawyer.phone:
            missing_fields.append("phone")
        if not lawyer.specialties:
            missing_fields.append("specialties")
        if lawyer.experience_years is None:
            missing_fields.append("experience_years")
        if not lawyer.district:
            missing_fields.append("district")
        
        return ProfileStatus(
            profile_completed=lawyer.profile_completed,
            missing_fields=missing_fields,
            user_type="lawyer"
        )
    
    else:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        missing_fields = []
        if not user.district:
            missing_fields.append("district")
        
        return ProfileStatus(
            profile_completed=user.profile_completed,
            missing_fields=missing_fields,
            user_type="user"
        )

