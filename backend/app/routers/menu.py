"""
Menu endpoints. Anyone (including customers, even unauthenticated)
can VIEW the menu. Only admin/staff can create, edit, or remove items.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.menu import MenuItem, Category
from app.schemas.menu import MenuItemOut, MenuItemCreate, MenuItemUpdate, CategoryOut, CategoryBase

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@router.post("/categories", response_model=CategoryOut, dependencies=[Depends(require_roles(["admin", "staff"]))])
def create_category(payload: CategoryBase, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="A category with this name already exists.")
    category = Category(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("", response_model=List[MenuItemOut])
def list_menu_items(category_id: Optional[int] = None, available_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(MenuItem)
    if category_id:
        query = query.filter(MenuItem.category_id == category_id)
    if available_only:
        query = query.filter(MenuItem.is_available == True)  # noqa: E712
    return query.all()


@router.get("/{item_id}", response_model=MenuItemOut)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found.")
    return item


@router.post("", response_model=MenuItemOut, dependencies=[Depends(require_roles(["admin", "staff"]))])
def create_menu_item(payload: MenuItemCreate, db: Session = Depends(get_db)):
    item = MenuItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=MenuItemOut, dependencies=[Depends(require_roles(["admin", "staff"]))])
def update_menu_item(item_id: int, payload: MenuItemUpdate, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", dependencies=[Depends(require_roles(["admin"]))])
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found.")
    db.delete(item)
    db.commit()
    return {"message": f"'{item.name}' removed from the menu."}
