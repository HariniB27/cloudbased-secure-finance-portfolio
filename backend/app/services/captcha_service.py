import requests
from app.config import get_settings

settings = get_settings()


class CaptchaService:
    @staticmethod
    def verify_recaptcha(token: str) -> bool:
        """Verify Google reCAPTCHA v3 token."""
        if not settings.RECAPTCHA_SECRET_KEY:
            # Allow local development only when secret is not configured.
            return settings.ENVIRONMENT == "development"

        if not token:
            return False

        try:
            response = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token,
                },
                timeout=8
            )
            data = response.json()
            return bool(
                data.get("success")
                and float(data.get("score", 0.0)) >= settings.RECAPTCHA_MIN_SCORE
            )
        except Exception:
            return False
