"""
Order endpoints.
  - Customers create orders for themselves.
  - Staff can create orders on behalf of walk-in customers (table orders).
  - Kitchen staff view/update order status (pending -> preparing -> ready -> served).
  - Admin/staff can view all orders; customers only see their own.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.menu import MenuItem
from app.models.order import Order, OrderItem, OrderStatus, OrderType
from app.schemas.order import OrderCreate, OrderOut, OrderItemOut, OrderStatusUpdate
from app.services.inventory_service import deduct_stock_for_menu_item
from app.services.email_service import send_order_confirmation_email

router = APIRouter(prefix="/orders", tags=["Orders"])


def _to_order_out(order: Order) -> OrderOut:
    items_out = []
    total = 0.0
    for oi in order.items:
        items_out.append(
            OrderItemOut(
                id=oi.id,
                menu_item_id=oi.menu_item_id,
                menu_item_name=oi.menu_item.name if oi.menu_item else "Unknown item",
                quantity=oi.quantity,
                unit_price=oi.unit_price,
                subtotal=oi.subtotal,
                special_request=oi.special_request,
            )
        )
        total += oi.subtotal

    out = OrderOut.model_validate(order)
    out.items = items_out
    out.total_amount = round(total, 2)
    return out


@router.post("", response_model=OrderOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="An order needs at least one item.")

    try:
        order_type_enum = OrderType(payload.order_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="order_type must be dine_in, takeaway, or delivery.")

    order = Order(
        customer_id=current_user.id if current_user.role.value == "customer" else None,
        created_by_staff_id=current_user.id if current_user.role.value in ("admin", "staff") else None,
        table_number=payload.table_number,
        order_type=order_type_enum,
        notes=payload.notes,
        status=OrderStatus.pending,
    )
    db.add(order)
    db.flush()  # get order.id without committing yet

    for line in payload.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == line.menu_item_id).first()
        if not menu_item:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Menu item {line.menu_item_id} not found.")
        if not menu_item.is_available:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"'{menu_item.name}' is currently unavailable.")

        db.add(OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=line.quantity,
            unit_price=menu_item.price,
            special_request=line.special_request,
        ))
        # Reduce ingredient stock for this sale
        deduct_stock_for_menu_item(db, menu_item.id, line.quantity, reason=f"order #{order.id}")

    db.commit()
    db.refresh(order)

    if current_user.email:
        # Use the items already attached to the order (avoids re-querying
        # and avoids the deprecated Query.get() API).
        total = sum(oi.subtotal for oi in order.items)
        send_order_confirmation_email(current_user.email, order.id, total)

    return _to_order_out(order)


@router.get("", response_model=List[OrderOut])
def list_orders(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Order)
    if current_user.role.value == "customer":
        query = query.filter(Order.customer_id == current_user.id)
    if status_filter:
        try:
            query = query.filter(Order.status == OrderStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status filter.")
    orders = query.order_by(Order.created_at.desc()).all()
    return [_to_order_out(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    if current_user.role.value == "customer" and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own orders.")
    return _to_order_out(order)


@router.patch(
    "/{order_id}/status",
    response_model=OrderOut,
    dependencies=[Depends(require_roles(["admin", "staff", "kitchen"]))],
)
def update_order_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    try:
        order.status = OrderStatus(payload.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status value.")
    db.commit()
    db.refresh(order)
    return _to_order_out(order)


@router.get(
    "/kitchen/queue",
    response_model=List[OrderOut],
    dependencies=[Depends(require_roles(["admin", "staff", "kitchen"]))],
)
def kitchen_queue(db: Session = Depends(get_db)):
    """Active orders the kitchen still needs to act on."""
    orders = (
        db.query(Order)
        .filter(Order.status.in_([OrderStatus.pending, OrderStatus.preparing]))
        .order_by(Order.created_at.asc())
        .all()
    )
    return [_to_order_out(o) for o in orders]
