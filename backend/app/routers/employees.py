"""
Employee management — admin only. Creating an employee also creates
the linked User account (role=staff or kitchen) so they can log in
immediately via email or mobile OTP.
"""
from typing import List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.user import User, UserRole
from app.models.employee import Employee, Attendance
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeOut, AttendanceMark

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
    dependencies=[Depends(require_roles(["admin"]))],
)


def _to_out(emp: Employee) -> EmployeeOut:
    return EmployeeOut(
        id=emp.id,
        user_id=emp.user_id,
        name=emp.user.name,
        email=emp.user.email,
        phone=emp.user.phone,
        role=emp.user.role.value,
        designation=emp.designation,
        salary=emp.salary,
        date_joined=emp.date_joined,
        shift=emp.shift,
    )


@router.get("", response_model=List[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return [_to_out(e) for e in db.query(Employee).all()]


@router.post("", response_model=EmployeeOut)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    if payload.role not in ("staff", "kitchen"):
        raise HTTPException(status_code=400, detail="Employee role must be 'staff' or 'kitchen'.")
    if not payload.email and not payload.phone:
        raise HTTPException(status_code=400, detail="An employee needs an email or phone number to log in.")

    if payload.email and db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="A user with this email already exists.")
    if payload.phone and db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="A user with this phone number already exists.")

    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        role=UserRole(payload.role),
        is_verified=False,
    )
    db.add(user)
    db.flush()

    employee = Employee(
        user_id=user.id,
        designation=payload.designation,
        salary=payload.salary,
        shift=payload.shift,
        date_joined=date.today(),
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return _to_out(employee)


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return _to_out(employee)


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")
    user = employee.user
    db.delete(employee)
    if user:
        user.is_active = False  # deactivate login rather than hard-delete history
    db.commit()
    return {"message": "Employee removed and account deactivated."}


@router.post("/attendance")
def mark_attendance(payload: AttendanceMark, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")

    today_record = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee.id, Attendance.date == date.today())
        .first()
    )
    if today_record:
        today_record.status = payload.status
    else:
        db.add(Attendance(employee_id=employee.id, status=payload.status, date=date.today()))
    db.commit()
    return {"message": f"Attendance marked '{payload.status}' for {employee.user.name}."}
