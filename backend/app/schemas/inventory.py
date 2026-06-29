from typing import Optional
from pydantic import BaseModel


class InventoryItemBase(BaseModel):
    name: str
    unit: str = "unit"
    quantity_in_stock: float = 0
    reorder_level: float = 5
    cost_per_unit: float = 0


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    quantity_in_stock: Optional[float] = None
    reorder_level: Optional[float] = None
    cost_per_unit: Optional[float] = None


class InventoryItemOut(InventoryItemBase):
    id: int
    is_low_stock: bool = False

    class Config:
        from_attributes = True


class StockAdjustRequest(BaseModel):
    """Used for manual restock or correction. Positive = add, negative = remove."""
    change_amount: float
    reason: str = "manual adjustment"
