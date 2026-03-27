from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import desc
import hashlib
import secrets
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.schemas.user import UserCreate, TokenData
from app.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    RESET_TOKEN_TTL_MINUTES = 15

    @staticmethod
    def _hash_reset_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[TokenData]:
        """Decode and verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id: int = payload.get("user_id")
            username: str = payload.get("sub")
            
            if username is None or user_id is None:
                return None
            
            return TokenData(user_id=user_id, username=username)
        except JWTError:
            return None

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = AuthService.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = AuthService.get_user_by_username(db, username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_password_reset_token(db: Session, user: User) -> str:
        """Create a one-time reset token valid for 15 minutes."""
        raw_token = secrets.token_urlsafe(48)
        token_hash = AuthService._hash_reset_token(raw_token)
        expiry = datetime.utcnow() + timedelta(minutes=AuthService.RESET_TOKEN_TTL_MINUTES)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expiry,
            used=False
        )
        db.add(reset_token)
        db.commit()
        return raw_token

    @staticmethod
    def reset_password_with_token(db: Session, raw_token: str, new_password: str) -> bool:
        """Consume a reset token and update user password."""
        token_hash = AuthService._hash_reset_token(raw_token)
        reset_token = (
            db.query(PasswordResetToken)
            .filter(PasswordResetToken.token_hash == token_hash)
            .order_by(desc(PasswordResetToken.created_at))
            .first()
        )

        if not reset_token:
            return False
        if reset_token.used:
            return False
        if reset_token.expires_at < datetime.utcnow():
            return False

        user = AuthService.get_user_by_id(db, reset_token.user_id)
        if not user:
            return False

        user.hashed_password = AuthService.get_password_hash(new_password)
        reset_token.used = True
        reset_token.used_at = datetime.utcnow()

        db.commit()
        return True
