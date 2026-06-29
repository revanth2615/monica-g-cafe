"""
User model. One table covers Admin, Staff, Kitchen, and Customer —
distinguished by the `role` column. This keeps auth logic in one place
while still letting each role have a different experience in the app.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    staff = "staff"
    kitchen = "kitchen"
    customer = "customer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(190), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)  # null for OTP-only / Google accounts
    role = Column(Enum(UserRole), default=UserRole.customer, nullable=False)
    google_id = Column(String(120), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="customer")
