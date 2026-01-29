from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from utils.auth import create_access_token
from utils.google_oauth import oauth
from fastapi.exceptions import HTTPException

router = APIRouter(prefix="/auth/google", tags=["Google Auth"])

@router.get("/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Google authentication failed")

    email = user_info["email"]

    user = db.query(User).filter(User.email == email).first()

    # Auto-create user if not exists
    if not user:
        user = User(
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            email=email,
            oauth_provider="google",
            oauth_id=user_info["sub"],
            email_verified=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
