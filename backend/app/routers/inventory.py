"""
Inventory endpoints — admin/staff only. Lets staff see current stock,
spot low-stock items, restock, and view the audit trail.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.inventory import InventoryItem
from app.schemas.inventory import InventoryItemOut, InventoryItemCreate, InventoryItemUpdate, StockAdjustRequest
from app.services.inventory_service import adjust_stock

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
    dependencies=[Depends(require_roles(["admin", "staff"]))],
)


def _to_out(item: InventoryItem) -> InventoryItemOut:
    out = InventoryItemOut.model_validate(item)
    out.is_low_stock = item.quantity_in_stock <= item.reorder_level
    return out


@router.get("", response_model=List[InventoryItemOut])
def list_inventory(low_stock_only: bool = False, db: Session = Depends(get_db)):
    items = db.query(InventoryItem).all()
    results = [_to_out(i) for i in items]
    if low_stock_only:
        results = [r for r in results if r.is_low_stock]
    return results


@router.post("", response_model=InventoryItemOut)
def create_inventory_item(payload: InventoryItemCreate, db: Session = Depends(get_db)):
    existing = db.query(InventoryItem).filter(InventoryItem.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="An inventory item with this name already exists.")
    item = InventoryItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_out(item)


@router.put("/{item_id}", response_model=InventoryItemOut)
def update_inventory_item(item_id: int, payload: InventoryItemUpdate, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return _to_out(item)


@router.post("/{item_id}/adjust", response_model=InventoryItemOut)
def adjust_inventory(item_id: int, payload: StockAdjustRequest, db: Session = Depends(get_db)):
    try:
        item = adjust_stock(db, item_id, payload.change_amount, payload.reason)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return _to_out(item)


@router.delete("/{item_id}")
def delete_inventory_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found.")
    db.delete(item)
    db.commit()
    return {"message": f"'{item.name}' removed from inventory."}
