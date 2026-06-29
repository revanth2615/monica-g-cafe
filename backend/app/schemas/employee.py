from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: str = "staff"  # staff | kitchen
    designation: str = "Staff"
    salary: float = 0
    shift: Optional[str] = None


class EmployeeUpdate(BaseModel):
    designation: Optional[str] = None
    salary: Optional[float] = None
    shift: Optional[str] = None


class EmployeeOut(BaseModel):
    id: int
    user_id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    designation: str
    salary: float
    date_joined: date
    shift: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceMark(BaseModel):
    employee_id: int
    status: str = "present"  # present | absent | leave
