from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import security
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, TokenRefreshRequest, TokenRefreshResponse, LogoutRequest
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not security.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    refresh_token = security.create_refresh_token(db=db, user_id=user.id)

    return {
        "status": "success",
        "token": access_token,
        "refresh_token": refresh_token,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.is_admin
        }
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user."""
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered"
        )
    
    hashed_password = security.get_password_hash(request.password)
    
    new_user = User(
        name=request.name,
        email=request.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Refresh the access token using a valid refresh token (Refresh Token Rotation)."""
    db_refresh = db.query(security.RefreshToken).filter(
        security.RefreshToken.token == request.refresh_token,
        security.RefreshToken.is_revoked == False
    ).first()

    if not db_refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    # Check expiry
    expires_at = db_refresh.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        db_refresh.is_revoked = True
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired refresh token")
    
    # Retrieve user
    user = db.query(User).filter(User.id == db_refresh.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    # Revoke the old refresh token (rotation)
    db_refresh.is_revoked = True
    db.commit()
    
    # Generate new access and refresh token pair
    access_token = security.create_access_token(data={"sub": user.email, "user_id": user.id})
    new_refresh_token = security.create_refresh_token(db=db, user_id=user.id)
    
    return {
        "status": "success",
        "token": access_token,
        "refresh_token": new_refresh_token,
        "message": "Token refreshed successfully"
    }

@router.post("/logout")
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
    token: str = Depends(security.oauth2_scheme)
):
    """Log out a user, blacklist their current access token, and revoke their refresh token."""
    try:
        payload = security.jwt.decode(token, security.settings.SECRET_KEY, algorithms=[security.settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
    except security.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if jti and exp:
        # Check if already blacklisted to prevent constraint errors
        existing = db.query(security.TokenBlacklist).filter(security.TokenBlacklist.jti == jti).first()
        if not existing:
            # Convert epoch timestamp to timezone-aware datetime
            exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
            db_blacklist = security.TokenBlacklist(jti=jti, expires_at=exp_datetime)
            db.add(db_blacklist)
    
    # Revoke the specific refresh token
    db_refresh = db.query(security.RefreshToken).filter(
        security.RefreshToken.token == request.refresh_token
    ).first()
    if db_refresh:
        db_refresh.is_revoked = True
    
    db.commit()
    return {"status": "success", "message": "Successfully logged out"}
