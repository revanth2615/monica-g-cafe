"""
Sends SMS OTPs via Twilio. Supports both the Verify API (recommended —
Twilio manages OTP generation/expiry for you) and a plain SMS fallback
using our own generated code from otp_service.

We use the plain-SMS path here so the SAME otp_service.create_otp() /
verify_otp() logic works identically for both email and mobile,
keeping one consistent OTP table and one set of rules.
"""
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.config import settings


def get_twilio_client() -> Client:
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def send_otp_sms(phone: str, otp_code: str) -> bool:
    try:
        client = get_twilio_client()
        client.messages.create(
            body=f"Your Monika G Cafe login code is {otp_code}. It expires in {settings.OTP_EXPIRE_MINUTES} minutes.",
            from_=settings.TWILIO_FROM_NUMBER,
            to=phone,
        )
        return True
    except TwilioRestException as exc:
        print(f"[sms_service] Twilio error sending to {phone}: {exc}")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"[sms_service] Unexpected error sending to {phone}: {exc}")
        return False
