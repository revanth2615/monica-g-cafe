"""
Billing endpoints — generates a bill from an order's items, applies tax
and discount, and tracks payment status. Admin/staff only (customers
see their bill via the order detail, not by managing it).
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles, get_current_user
from app.models.user import User
from app.models.order import Order, Bill
from app.schemas.order import BillOut, BillCreate, BillPaymentUpdate

router = APIRouter(prefix="/bills", tags=["Billing"])


def _to_bill_out(bill: Bill) -> BillOut:
    out = BillOut.model_validate(bill)
    out.is_paid = bool(bill.is_paid)
    return out


@router.post("", response_model=BillOut, dependencies=[Depends(require_roles(["admin", "staff"]))])
def generate_bill(payload: BillCreate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    if order.bill:
        raise HTTPException(status_code=400, detail="A bill already exists for this order.")

    subtotal = round(sum(oi.subtotal for oi in order.items), 2)
    tax_amount = round(subtotal * (payload.tax_percent / 100), 2)
    total = round(subtotal + tax_amount - payload.discount_amount, 2)

    bill = Bill(
        order_id=order.id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=payload.discount_amount,
        total_amount=total,
        payment_method=payload.payment_method,
        is_paid=0,
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return _to_bill_out(bill)


@router.get("", response_model=List[BillOut], dependencies=[Depends(require_roles(["admin", "staff"]))])
def list_bills(unpaid_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Bill)
    if unpaid_only:
        query = query.filter(Bill.is_paid == 0)
    return [_to_bill_out(b) for b in query.order_by(Bill.created_at.desc()).all()]


@router.get("/{bill_id}", response_model=BillOut)
def get_bill(bill_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found.")
    if current_user.role.value == "customer" and bill.order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own bills.")
    return _to_bill_out(bill)


@router.patch("/{bill_id}/payment", response_model=BillOut, dependencies=[Depends(require_roles(["admin", "staff"]))])
def update_payment(bill_id: int, payload: BillPaymentUpdate, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found.")
    bill.is_paid = 1 if payload.is_paid else 0
    if payload.payment_method:
        bill.payment_method = payload.payment_method
    db.commit()
    db.refresh(bill)
    return _to_bill_out(bill)
