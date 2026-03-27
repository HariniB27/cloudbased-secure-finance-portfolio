from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.services.auth_service import AuthService
from app.services.captcha_service import CaptchaService
from app.services.email_service import EmailService
from app.config import get_settings
from app.services.asset_service import AssetService
from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    if not CaptchaService.verify_recaptcha(user_data.recaptcha_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Captcha validation failed")
    
    # Check if username exists
    if AuthService.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if AuthService.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        user = AuthService.create_user(db, user_data)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed"
        )


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    if not CaptchaService.verify_recaptcha(user_data.recaptcha_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Captcha validation failed")
    
    user = AuthService.authenticate_user(db, user_data.username, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )

    # Auto-refresh portfolio on login (best-effort)
    try:
        AssetService.refresh_asset_prices(db, user.id)
    except Exception as e:
        print(f"Portfolio auto-refresh failed for user={user.id}: {e}")
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Create a reset token (always return generic response)."""
    if not CaptchaService.verify_recaptcha(payload.recaptcha_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Captcha validation failed")

    dev_response = {"message": "If an account exists, a reset link has been sent."}
    user = AuthService.get_user_by_email(db, payload.email)
    if user:
        token = AuthService.create_password_reset_token(db, user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        email_sent = EmailService.send_password_reset_email(user.email, reset_link)
        print(f"[PASSWORD_RESET_EMAIL] user={user.email} sent={email_sent}")
        if settings.ENVIRONMENT == "development":
            dev_response["reset_link"] = reset_link

    return dev_response


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using one-time, 15-minute token."""
    if not CaptchaService.verify_recaptcha(payload.recaptcha_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Captcha validation failed")

    success = AuthService.reset_password_with_token(db, payload.token, payload.new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    return {"message": "Password reset successful."}
