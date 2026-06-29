"""
Inventory: raw stock items (e.g. milk, coffee beans, cups) and a link
table that says how much of each ingredient a menu item consumes.
This is what lets a sale automatically reduce stock.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True)
    unit = Column(String(20), nullable=False, default="unit")  # kg, ltr, pcs, etc.
    quantity_in_stock = Column(Float, nullable=False, default=0)
    reorder_level = Column(Float, nullable=False, default=5)  # triggers low-stock alert
    cost_per_unit = Column(Float, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recipe_links = relationship("MenuItemIngredient", back_populates="inventory_item")


class MenuItemIngredient(Base):
    """How much of an inventory item is consumed per 1 unit of a menu item."""
    __tablename__ = "menu_item_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity_required = Column(Float, nullable=False)

    menu_item = relationship("MenuItem", back_populates="recipe_links")
    inventory_item = relationship("InventoryItem", back_populates="recipe_links")


class StockLog(Base):
    """Audit trail every time stock changes (restock or consumption)."""
    __tablename__ = "stock_logs"

    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    change_amount = Column(Float, nullable=False)  # positive = restock, negative = consumed
    reason = Column(String(120), nullable=False)  # "order #123", "manual restock", etc.
    created_at = Column(DateTime, default=datetime.utcnow)
