"""
Inventory Service – Firestore CRUD + computed warning fields.

Collection: pharmacy_inventory/{id}
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import HTTPException
from app.core.firebase import firebase_service

INVENTORY_COLLECTION = "pharmacy_inventory"

LOW_STOCK_THRESHOLD = 10      # default; overridden per-item via `threshold`
EXPIRY_WINDOW_DAYS = 30       # items expiring within this window get flagged


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _ts_to_iso(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    if isinstance(dt, str):
        return dt
    if dt.tzinfo is None:
        return dt.isoformat() + "Z"
    return dt.isoformat()


# ──────────────────────────────────────────────
# Computed flags
# ──────────────────────────────────────────────

def _enrich_item(d: dict, doc_id: str) -> dict:
    """Attach `is_low_stock` and `is_expiring_soon` booleans."""
    quantity = d.get("quantity", 0)
    threshold = d.get("threshold", LOW_STOCK_THRESHOLD)
    expiry = d.get("expiry_date")

    # Handle Firestore Timestamp objects and strings
    if expiry and not isinstance(expiry, datetime):
        try:
            dt = datetime.fromisoformat(str(expiry).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            expiry = dt
        except Exception:
            expiry = None

    # Ensure expiry is timezone-aware if it's a datetime
    if isinstance(expiry, datetime) and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    is_low = quantity < threshold
    is_expiring = False
    if expiry:
        is_expiring = (expiry - _now()).days < EXPIRY_WINDOW_DAYS

    return {
        "id": doc_id,
        "drug_name": d.get("drug_name", ""),
        "strength": d.get("strength", ""),
        "quantity": quantity,
        "expiry_date": _ts_to_iso(expiry) if isinstance(expiry, datetime) else str(expiry) if expiry else None,
        "batch_number": d.get("batch_number", ""),
        "threshold": threshold,
        "is_low_stock": is_low,
        "is_expiring_soon": is_expiring,
        "price": d.get("price", 0.0),
    }


# ──────────────────────────────────────────────
# 1. List inventory  (sorted by expiry_date ASC)
# ──────────────────────────────────────────────

async def list_inventory() -> List[dict]:
    try:
        if firebase_service.mock_mode:
            return _mock_inventory()

        db = firebase_service.db
        docs = (
            db.collection(INVENTORY_COLLECTION)
            .order_by("expiry_date")
            .stream()
        )
        return [_enrich_item(doc.to_dict(), doc.id) for doc in docs]
    except Exception as e:
        import traceback
        print(f"DEBUG: list_inventory error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────
# 2. Update stock quantity
# ──────────────────────────────────────────────

async def update_stock(item_id: str, new_quantity: int) -> Optional[dict]:
    if firebase_service.mock_mode:
        return _mock_update_stock(item_id, new_quantity)

    db = firebase_service.db
    ref = db.collection(INVENTORY_COLLECTION).document(item_id)
    doc = ref.get()
    if not doc.exists:
        return None

    ref.update({"quantity": new_quantity})
    updated = ref.get().to_dict()
    return _enrich_item(updated, item_id)


# ──────────────────────────────────────────────
# 3. Add inventory item
# ──────────────────────────────────────────────

async def add_item(data: dict) -> dict:
    if firebase_service.mock_mode:
        return _mock_add_item(data)

    db = firebase_service.db
    
    # Parse expiry_date string to datetime for Firestore
    expiry_str = data.get("expiry_date")
    if expiry_str:
        try:
            dt = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
            data["expiry_date"] = dt
        except ValueError:
            pass  # Keep as string or handle error if strict validation needed

    # Generate a new document reference
    new_ref = db.collection(INVENTORY_COLLECTION).document()
    doc_id = new_ref.id
    
    new_ref.set(data)
    
    # Return enriched item
    return _enrich_item(data, doc_id)


# ──────────────────────────────────────────────
# 4. Delete inventory item
# ──────────────────────────────────────────────

async def delete_item(item_id: str) -> bool:
    if firebase_service.mock_mode:
        return _mock_delete_item(item_id)

    db = firebase_service.db
    ref = db.collection(INVENTORY_COLLECTION).document(item_id)
    doc = ref.get()
    if not doc.exists:
        return False

    ref.delete()
    return True


# ──────────────────────────────────────────────
# Mock data
# ──────────────────────────────────────────────

# ──────────────────────────────────────────────
# Mock data
# ──────────────────────────────────────────────

from pharmacy.mock_data import get_initial_mock_inventory

# Initialize mock inventory
_MOCK_INVENTORY_DB = get_initial_mock_inventory()

def _mock_inventory() -> List[dict]:
    # Return directly from global state to allow updates to persist in memory
    return _MOCK_INVENTORY_DB


def _mock_update_stock(item_id: str, new_quantity: int) -> Optional[dict]:
    print(f"[MOCK] Inventory {item_id} quantity → {new_quantity}")
    
    for item in _MOCK_INVENTORY_DB:
        if item["id"] == item_id:
            item["quantity"] = new_quantity
            item["is_low_stock"] = new_quantity < item["threshold"]
            # Enriched return
            return item
            
    return None


def _mock_add_item(data: dict) -> dict:
    item_id = str(uuid.uuid4())
    print(f"[MOCK] Added Inventory {item_id}: {data}")
    
    # Simulate enrichment
    enriched = data.copy()
    enriched["id"] = item_id
    
    # Calculate computed fields
    quantity = data.get("quantity", 0)
    threshold = data.get("threshold", 10)
    
    # Handle expiry date for mock calculation
    expiry = data.get("expiry_date") # string
    is_expiring = False
    if expiry:
        try:
            dt = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            is_expiring = (dt - _now()).days < EXPIRY_WINDOW_DAYS
        except:
            pass

    enriched["is_low_stock"] = quantity < threshold
    enriched["is_expiring_soon"] = is_expiring
    
    _MOCK_INVENTORY_DB.append(enriched)
    # Re-sort by expiry
    _MOCK_INVENTORY_DB.sort(key=lambda x: x.get("expiry_date") or "")
    
    return enriched


def _mock_delete_item(item_id: str) -> bool:
    print(f"[MOCK] Deleted Inventory {item_id}")
    initial_len = len(_MOCK_INVENTORY_DB)
    # Remove item from list
    _MOCK_INVENTORY_DB[:] = [item for item in _MOCK_INVENTORY_DB if item["id"] != item_id]
    return len(_MOCK_INVENTORY_DB) < initial_len

