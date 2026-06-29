"""
Pydantic schemas for authentication: signup, OTP requests/verification,
Google login, and the token response shape the frontend expects.

IMPORTANT: these field names are the contract between frontend and backend.
The frontend JS sends JSON bodies that must match these exactly.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class SignupRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = "customer"  # admin creates staff/kitchen accounts explicitly

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v):
        if v and not v.startswith("+"):
            raise ValueError("Phone number must be in E.164 format, e.g. +919876543210")
        return v


class EmailOTPRequest(BaseModel):
    """Step 1 of email login: ask the server to send an OTP to this email."""
    email: EmailStr


class EmailOTPVerify(BaseModel):
    """Step 2 of email login: prove you received the OTP."""
    email: EmailStr
    otp_code: str


class MobileOTPRequest(BaseModel):
    """Step 1 of mobile login: ask the server to send an OTP via SMS."""
    phone: str

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v):
        if not v.startswith("+"):
            raise ValueError("Phone number must be in E.164 format, e.g. +919876543210")
        return v


class MobileOTPVerify(BaseModel):
    phone: str
    otp_code: str


class GoogleLoginRequest(BaseModel):
    """Frontend sends the ID token it got from Google's sign-in widget."""
    id_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserPublic"


class UserPublic(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_verified: bool

    class Config:
        from_attributes = True


class RefreshRequest(BaseModel):
    refresh_token: str
