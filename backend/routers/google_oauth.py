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
    """
    redirect_uri = request.url_for("google_callback")
    # Store user_type in session/state for callback
    return await oauth.google.authorize_redirect(
        request, 
        redirect_uri,
        state=user_type  # Pass user_type as state
    )


@router.get("/callback", name="google_callback")
async def google_callback(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback
    
    Creates or logs in user/lawyer based on state parameter
    """
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(status_code=400, detail="Google authentication failed")

        email = user_info["email"]
        
        # Get user_type from state parameter (defaults to 'user')
        user_type = request.query_params.get("state", "user")

        if user_type == "lawyer":
            # Handle lawyer OAuth login/registration
            lawyer = db.query(Lawyer).filter(Lawyer.email == email).first()

            if not lawyer:
                # Auto-create lawyer profile with OAuth (incomplete profile)
                lawyer = Lawyer(
                    name=user_info.get("name", f"{user_info.get('given_name', '')} {user_info.get('family_name', '')}".strip()),
                    email=email,
                    phone=None,  # To be filled in profile completion
                    specialties=None,  # To be filled in profile completion
                    experience_years=None,  # To be filled in profile completion
                    district=None,  # To be filled in profile completion
                    oauth_provider="google",
                    oauth_id=user_info["sub"],
                    is_email_verified=True,
                    is_active=True,
                    password_hash=None,  # No password for OAuth users
                    profile_completed=False  # Profile needs completion
                )
                db.add(lawyer)
                db.commit()
                db.refresh(lawyer)

            # Create access token for lawyer
            access_token = create_access_token({
                "sub": str(lawyer.id),
                "role": "lawyer",
                "email": lawyer.email,
            })

            # Determine redirect URL based on profile completion status
            frontend_url = config.Settings.CORS_ORIGINS[0] if config.Settings.CORS_ORIGINS else "http://localhost:5173"
            
            if not lawyer.profile_completed:
                # Redirect to profile completion page
                return RedirectResponse(
                    url=f"{frontend_url}/lawyer/complete-profile?token={access_token}&type=lawyer&new_user=true"
                )
            else:
                # Redirect to lawyer dashboard
                return RedirectResponse(
                    url=f"{frontend_url}/lawyer/oauth-callback?token={access_token}&type=lawyer"
                )

        else:
            # Handle user OAuth login/registration
            user = db.query(User).filter(User.email == email).first()

            if not user:
                # Auto-create user if not exists (incomplete profile)
                user = User(
                    first_name=user_info.get("given_name", ""),
                    last_name=user_info.get("family_name", ""),
                    email=email,
                    oauth_provider="google",
                    oauth_id=user_info["sub"],
                    email_verified=True,
                    is_active=True,
                    role="user",
                    password_hash=None,  # No password for OAuth users
                    preferred_language="en",  # Default
                    district=None,  # To be filled in profile completion
                    profile_completed=False  # Profile needs completion
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # Create access token for user
            access_token = create_access_token({
                "sub": str(user.id),
                "role": user.role,
                "email": user.email,
            })

            # Determine redirect URL based on profile completion status
            frontend_url = config.Settings.CORS_ORIGINS[0] if config.Settings.CORS_ORIGINS else "http://localhost:5173"
            
            if not user.profile_completed:
                # Redirect to profile completion page
                return RedirectResponse(
                    url=f"{frontend_url}/complete-profile?token={access_token}&type=user&new_user=true"
                )
            else:
                # Redirect to user dashboard
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

