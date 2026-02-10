"""
FastAPI Router – Pharmacy Inventory
Prefix: /pharmacy/inventory

Endpoints:
  GET  /pharmacy/inventory              → Full inventory sorted by expiry (soonest first)
  POST /pharmacy/inventory/update       → Update stock quantity for an item
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from pharmacy.schemas import (
    InventoryItemResponse,
    UpdateStockRequest,
    AddInventoryRequest,
)
from pharmacy import inventory_service as svc

router = APIRouter(prefix="/pharmacy/inventory", tags=["Pharmacy Inventory"])


# ──────────────────────────────────────────────
# 1. List inventory (sorted by expiry, with warnings)
# ──────────────────────────────────────────────

@router.get("", response_model=List[InventoryItemResponse])
async def list_inventory():
    """
    Return full inventory table.
    Sorted by `expiry_date` ascending (soonest first).
    Each row includes computed:
    - **is_low_stock** (Red warning if quantity < threshold)
    - **is_expiring_soon** (Yellow warning if expiry < 30 days)
    """
    return await svc.list_inventory()


# ──────────────────────────────────────────────
# 2. Add new inventory item
# ──────────────────────────────────────────────

@router.post("/add", response_model=InventoryItemResponse)
async def add_item(body: AddInventoryRequest):
    """Add a new item to the inventory."""
    return await svc.add_item(body.dict())


# ──────────────────────────────────────────────
# 3. Update stock quantity
# ──────────────────────────────────────────────

@router.post("/update", response_model=InventoryItemResponse)
async def update_stock(body: UpdateStockRequest):
    """Set the stock quantity for a given inventory item."""
    result = await svc.update_stock(body.item_id, body.quantity)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Inventory item {body.item_id} not found")
    return result


# ──────────────────────────────────────────────
# 4. Delete inventory item
# ──────────────────────────────────────────────

@router.delete("/{item_id}")
async def delete_item(item_id: str):
    """Delete an inventory item."""
    deleted = await svc.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Inventory item {item_id} not found")
    return {"id": item_id, "status": "deleted"}
