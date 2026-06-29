"""
Employee profile data, linked 1-to-1 with a User account that has
role = staff or kitchen. Keeping this separate from User means HR-style
fields don't clutter the auth table.
"""
from datetime import date, datetime

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    designation = Column(String(80), nullable=False, default="Staff")
    salary = Column(Float, nullable=False, default=0)
    date_joined = Column(Date, default=date.today)
    shift = Column(String(40), nullable=True)  # e.g. "Morning 8am-4pm"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    attendance = relationship("Attendance", back_populates="employee")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, default=date.today)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    status = Column(String(20), default="present")  # present, absent, leave

    employee = relationship("Employee", back_populates="attendance")
