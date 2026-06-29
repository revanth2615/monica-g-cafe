"""
Reporting endpoints — admin/staff only. Aggregates sales, order counts,
and low-stock alerts for the dashboard.
"""
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.order import Order, OrderItem, Bill, OrderStatus
from app.models.inventory import InventoryItem
from app.models.menu import MenuItem

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(require_roles(["admin", "staff"]))],
)


@router.get("/dashboard")
def dashboard_summary(db: Session = Depends(get_db)):
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())

    orders_today = db.query(Order).filter(Order.created_at >= start_of_day).count()
    revenue_today = (
        db.query(func.coalesce(func.sum(Bill.total_amount), 0))
        .join(Order, Order.id == Bill.order_id)
        .filter(Order.created_at >= start_of_day, Bill.is_paid == 1)
        .scalar()
    )
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.pending).count()
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.quantity_in_stock <= InventoryItem.reorder_level
    ).count()
    unpaid_bills = db.query(Bill).filter(Bill.is_paid == 0).count()

    return {
        "orders_today": orders_today,
        "revenue_today": round(float(revenue_today or 0), 2),
        "pending_orders": pending_orders,
        "low_stock_items": low_stock_items,
        "unpaid_bills": unpaid_bills,
    }


@router.get("/sales")
def sales_report(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    query = db.query(Bill).filter(Bill.is_paid == 1)
    if start_date:
        query = query.filter(Bill.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        query = query.filter(Bill.created_at <= datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1))

    bills = query.all()
    total_revenue = round(sum(b.total_amount for b in bills), 2)
    total_tax = round(sum(b.tax_amount for b in bills), 2)
    total_discount = round(sum(b.discount_amount for b in bills), 2)

    return {
        "bill_count": len(bills),
        "total_revenue": total_revenue,
        "total_tax_collected": total_tax,
        "total_discount_given": total_discount,
    }


@router.get("/top-items")
def top_selling_items(limit: int = 5, db: Session = Depends(get_db)):
    results = (
        db.query(
            MenuItem.name,
            func.sum(OrderItem.quantity).label("total_sold"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_revenue"),
        )
        .join(OrderItem, OrderItem.menu_item_id == MenuItem.id)
        .group_by(MenuItem.id, MenuItem.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )
    return [
        {"name": r.name, "total_sold": int(r.total_sold), "total_revenue": round(float(r.total_revenue), 2)}
        for r in results
    ]
