"""
Authentication endpoints.

Three ways to log in, as required:
  1. Email + OTP  -> POST /auth/email/request-otp, then /auth/email/verify-otp
  2. Mobile + OTP -> POST /auth/mobile/request-otp, then /auth/mobile/verify-otp
  3. Google login -> POST /auth/google

Email login ALWAYS requires OTP — there is no password-based email login
anywhere in this API, matching the requirement that email login must use OTP.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.otp import OTPPurpose
from app.schemas.auth import (
    EmailOTPRequest, EmailOTPVerify,
    MobileOTPRequest, MobileOTPVerify,
    GoogleLoginRequest, TokenResponse, UserPublic, RefreshRequest,
)
from app.services.otp_service import create_otp, verify_otp
from app.services.email_service import send_otp_email
from app.services.sms_service import send_otp_sms
from app.services.google_oauth import verify_google_token
from app.services.security import create_access_token, create_refresh_token, decode_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _issue_tokens(user: User) -> TokenResponse:
    token_data = {"sub": str(user.id), "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserPublic.model_validate(user),
    )


# ---------- EMAIL LOGIN (OTP always required) ----------

@router.post("/email/request-otp", status_code=status.HTTP_200_OK)
def request_email_otp(payload: EmailOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Auto-create a customer account on first-ever email login attempt
        user = User(name=payload.email.split("@")[0], email=payload.email, role=UserRole.customer)
        db.add(user)
        db.commit()
        db.refresh(user)

    code = create_otp(db, identifier=payload.email, purpose=OTPPurpose.login)
    sent = send_otp_email(payload.email, code)
    if not sent:
        raise HTTPException(status_code=502, detail="Could not send the OTP email. Please try again.")
    return {"message": f"OTP sent to {payload.email}."}


@router.post("/email/verify-otp", response_model=TokenResponse)
def verify_email_otp(payload: EmailOTPVerify, db: Session = Depends(get_db)):
    if not verify_otp(db, identifier=payload.email, code=payload.otp_code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found for this email.")

    user.is_verified = True
    db.commit()
    return _issue_tokens(user)


# ---------- MOBILE LOGIN (OTP) ----------

@router.post("/mobile/request-otp", status_code=status.HTTP_200_OK)
def request_mobile_otp(payload: MobileOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user:
        user = User(name=f"User {payload.phone[-4:]}", phone=payload.phone, role=UserRole.customer)
        db.add(user)
        db.commit()
        db.refresh(user)

    code = create_otp(db, identifier=payload.phone, purpose=OTPPurpose.login)
    sent = send_otp_sms(payload.phone, code)
    if not sent:
        raise HTTPException(status_code=502, detail="Could not send the OTP SMS. Please try again.")
    return {"message": f"OTP sent to {payload.phone}."}


@router.post("/mobile/verify-otp", response_model=TokenResponse)
def verify_mobile_otp(payload: MobileOTPVerify, db: Session = Depends(get_db)):
    if not verify_otp(db, identifier=payload.phone, code=payload.otp_code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found for this phone number.")

    user.is_verified = True
    db.commit()
    return _issue_tokens(user)


# ---------- GOOGLE LOGIN ----------

@router.post("/google", response_model=TokenResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    info = verify_google_token(payload.id_token)
    if not info or not info.get("email"):
        raise HTTPException(status_code=401, detail="Invalid Google token.")

    user = db.query(User).filter(User.email == info["email"]).first()
    if not user:
        user = User(
            name=info["name"],
            email=info["email"],
            google_id=info["google_id"],
            role=UserRole.customer,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.google_id:
        user.google_id = info["google_id"]
        user.is_verified = True
        db.commit()

    return _issue_tokens(user)


# ---------- TOKEN REFRESH ----------

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    user = db.query(User).filter(User.id == int(decoded["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")

    return _issue_tokens(user)


# ---------- CURRENT USER ----------

@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
