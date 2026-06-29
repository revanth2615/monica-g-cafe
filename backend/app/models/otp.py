"""
Stores one-time passwords for both email and mobile login.
Each row is a single OTP attempt tied to an identifier (email or phone).
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum

from app.database import Base


class OTPPurpose(str, enum.Enum):
    login = "login"
    signup = "signup"
    password_reset = "password_reset"


class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(190), index=True, nullable=False)  # email or phone
    code = Column(String(10), nullable=False)
    purpose = Column(Enum(OTPPurpose), default=OTPPurpose.login)
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
