"""
Import every model here so Base.metadata sees all tables when
create_all() runs, and so other modules can do `from app.models import User`.
"""
from app.models.user import User, UserRole
from app.models.otp import OTP, OTPPurpose
from app.models.menu import Category, MenuItem
from app.models.inventory import InventoryItem, MenuItemIngredient, StockLog
from app.models.order import Order, OrderItem, Bill, OrderStatus, OrderType
from app.models.employee import Employee, Attendance

__all__ = [
    "User", "UserRole",
    "OTP", "OTPPurpose",
    "Category", "MenuItem",
    "InventoryItem", "MenuItemIngredient", "StockLog",
    "Order", "OrderItem", "Bill", "OrderStatus", "OrderType",
    "Employee", "Attendance",
]
