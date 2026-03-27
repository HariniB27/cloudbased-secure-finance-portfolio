from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://portfolio_user:portfolio_pass@localhost:5432/portfolio_db"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # AWS Bedrock (optional)
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "models/gemini-2.5-flash"
    
    # Google reCAPTCHA v3
    RECAPTCHA_SECRET_KEY: str = ""
    RECAPTCHA_MIN_SCORE: float = 0.5
    
    # SMTP (forgot-password email delivery)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: str = ""
    
    # App
    USE_MOCK_LLM: bool = False
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
