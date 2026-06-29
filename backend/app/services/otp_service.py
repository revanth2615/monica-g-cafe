"""
Generates and verifies OTPs for both email and mobile login.
Shared by both flows so the rules (expiry, attempt limit, single-use)
are enforced consistently in one place.
"""
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models.otp import OTP, OTPPurpose

MAX_ATTEMPTS = 5


def generate_otp_code() -> str:
    digits = "0123456789"
    return "".join(random.choice(digits) for _ in range(settings.OTP_LENGTH))


def create_otp(db: Session, identifier: str, purpose: OTPPurpose = OTPPurpose.login) -> str:
    """Invalidate previous unused OTPs for this identifier, then create a fresh one."""
    db.query(OTP).filter(
        OTP.identifier == identifier,
        OTP.is_used == False,  # noqa: E712
    ).update({"is_used": True})

    code = generate_otp_code()
    otp = OTP(
        identifier=identifier,
        code=code,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
    )
    db.add(otp)
    db.commit()
    return code


def verify_otp(db: Session, identifier: str, code: str) -> bool:
    otp = (
        db.query(OTP)
        .filter(OTP.identifier == identifier, OTP.is_used == False)  # noqa: E712
        .order_by(OTP.created_at.desc())
        .first()
    )
    if not otp:
        return False
    if otp.attempts >= MAX_ATTEMPTS:
        return False
    if otp.expires_at < datetime.utcnow():
        return False

    if otp.code != code:
        otp.attempts += 1
        db.commit()
        return False

    otp.is_used = True
    db.commit()
    return True
