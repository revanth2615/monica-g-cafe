"""
Sends emails via SMTP — used for OTP login codes and order/billing
notifications. Wrapped in try/except so a flaky SMTP server doesn't
crash the request; failures are logged instead.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[email_service] Failed to send email to {to_email}: {exc}")
        return False


def send_otp_email(to_email: str, otp_code: str) -> bool:
    subject = "Your Monika G Cafe login code"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
        <h2 style="color:#6B3F1D;">Monika G Cafe</h2>
        <p>Your one-time login code is:</p>
        <p style="font-size: 28px; font-weight: bold; letter-spacing: 4px;">{otp_code}</p>
        <p>This code expires in {settings.OTP_EXPIRE_MINUTES} minutes. If you didn't request this, you can ignore this email.</p>
    </div>
    """
    return send_email(to_email, subject, body)


def send_order_confirmation_email(to_email: str, order_id: int, total: float) -> bool:
    subject = f"Order #{order_id} confirmed — Monika G Cafe"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto;">
        <h2 style="color:#6B3F1D;">Monika G Cafe</h2>
        <p>Your order <strong>#{order_id}</strong> has been received.</p>
        <p>Total: <strong>₹{total:.2f}</strong></p>
        <p>We'll notify you when it's ready.</p>
    </div>
    """
    return send_email(to_email, subject, body)
