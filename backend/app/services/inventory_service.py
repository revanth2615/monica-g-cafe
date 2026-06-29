"""
Stock-affecting logic shared between the inventory router and the
order router. Keeping it here means "place an order" and "manually
adjust stock" both go through the same audited path.
"""
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem, MenuItemIngredient, StockLog


def adjust_stock(db: Session, inventory_item_id: int, change_amount: float, reason: str) -> InventoryItem:
    item = db.query(InventoryItem).filter(InventoryItem.id == inventory_item_id).first()
    if not item:
        raise ValueError(f"Inventory item {inventory_item_id} not found.")

    item.quantity_in_stock = round(item.quantity_in_stock + change_amount, 3)
    db.add(StockLog(inventory_item_id=item.id, change_amount=change_amount, reason=reason))
    db.commit()
    db.refresh(item)
    return item


def deduct_stock_for_menu_item(db: Session, menu_item_id: int, quantity_ordered: int, reason: str) -> None:
    """
    When `quantity_ordered` units of a menu item are sold, walk its
    recipe (MenuItemIngredient) and reduce each ingredient's stock.
    Silently skips items with no recipe defined (not all cafes track
    inventory at ingredient level for every item).
    """
    links = db.query(MenuItemIngredient).filter(MenuItemIngredient.menu_item_id == menu_item_id).all()
    for link in links:
        total_needed = link.quantity_required * quantity_ordered
        adjust_stock(db, link.inventory_item_id, -total_needed, reason)
