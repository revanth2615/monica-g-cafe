from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1
    special_request: Optional[str] = None


class OrderCreate(BaseModel):
    table_number: Optional[str] = None
    order_type: str = "dine_in"  # dine_in | takeaway | delivery
    notes: Optional[str] = None
    items: List[OrderItemCreate]


class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    menu_item_name: str
    quantity: int
    unit_price: float
    subtotal: float
    special_request: Optional[str] = None

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    customer_id: Optional[int] = None
    table_number: Optional[str] = None
    order_type: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    items: List[OrderItemOut] = []
    total_amount: float = 0

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: str  # pending | preparing | ready | served | cancelled


class BillOut(BaseModel):
    id: int
    order_id: int
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    payment_method: Optional[str] = None
    is_paid: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BillCreate(BaseModel):
    order_id: int
    discount_amount: float = 0
    tax_percent: float = 5.0
    payment_method: Optional[str] = "cash"


class BillPaymentUpdate(BaseModel):
    is_paid: bool
    payment_method: Optional[str] = None
