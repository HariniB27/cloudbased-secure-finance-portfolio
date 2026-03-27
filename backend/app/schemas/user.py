from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    recaptcha_token: str


class UserLogin(BaseModel):
    username: str
    password: str
    recaptcha_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    recaptcha_token: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    recaptcha_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    username: str
