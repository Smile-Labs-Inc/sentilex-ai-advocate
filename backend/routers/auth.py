from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.auth import SignupRequest, LoginRequest, AuthResponse
from utils.auth import hash_password, verify_password, create_access_token
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])


#signup endpoint
@router.post("/signup", status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        preferred_language=payload.preferred_language,
        district=payload.district,
    )

    db.add(user)
    db.commit()
    return {"message": "User created successfully"}


#signin endpoint
@router.post("/signin", response_model=AuthResponse)
def signin(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    user.last_login_at = datetime.utcnow()
    user.failed_login_attempts = 0
    db.commit()

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    return AuthResponse(access_token=token)
