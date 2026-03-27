import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings

settings = get_settings()


class EmailService:
    """SMTP email sender for account notifications."""

    @staticmethod
    def is_configured() -> bool:
        return bool(
            settings.SMTP_HOST
            and settings.SMTP_USERNAME
            and settings.SMTP_PASSWORD
            and settings.SMTP_FROM_EMAIL
        )

    @staticmethod
    def send_password_reset_email(to_email: str, reset_link: str) -> bool:
        """Send password reset email using configured SMTP server."""
        if not EmailService.is_configured():
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = "Portfolio Manager - Password Reset"
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = to_email

        text_body = (
            "You requested a password reset for your Portfolio Manager account.\n\n"
            f"Reset link: {reset_link}\n\n"
            "This link expires in 15 minutes and can be used only once.\n"
            "If you did not request this, please ignore this email."
        )
        html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #111827;">
    <h3 style="margin-bottom: 8px;">Password Reset Request</h3>
    <p>You requested a password reset for your Portfolio Manager account.</p>
    <p>
      <a href="{reset_link}" style="display:inline-block;padding:10px 14px;background:#2563eb;color:#fff;text-decoration:none;border-radius:6px;">
        Reset Password
      </a>
    </p>
    <p style="margin-top: 12px;">This link expires in <b>15 minutes</b> and can be used only once.</p>
    <p>If you did not request this, please ignore this email.</p>
  </body>
</html>
"""
        message.attach(MIMEText(text_body, "plain"))
        message.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], message.as_string())
            return True
        except Exception as e:
            print(f"Email send failed for {to_email}: {e}")
            return False
