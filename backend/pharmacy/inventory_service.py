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

def _mock_inventory() -> List[dict]:
    now = _now()
    seed = [
        # Existing Items
        {"id": "INV-001", "drug_name": "Amoxicillin", "strength": "500mg", "quantity": 120, "expiry_date": _ts_to_iso(now + timedelta(days=180)), "batch_number": "BTX-20260101", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-002", "drug_name": "Paracetamol", "strength": "650mg", "quantity": 8, "expiry_date": _ts_to_iso(now + timedelta(days=90)), "batch_number": "BTX-20251210", "threshold": 10, "is_low_stock": True, "is_expiring_soon": False},
        {"id": "INV-003", "drug_name": "Pantoprazole", "strength": "40mg", "quantity": 45, "expiry_date": _ts_to_iso(now + timedelta(days=15)), "batch_number": "BTX-20250801", "threshold": 10, "is_low_stock": False, "is_expiring_soon": True},
        {"id": "INV-004", "drug_name": "Cetirizine", "strength": "10mg", "quantity": 3, "expiry_date": _ts_to_iso(now + timedelta(days=10)), "batch_number": "BTX-20250601", "threshold": 10, "is_low_stock": True, "is_expiring_soon": True},
        {"id": "INV-005", "drug_name": "Metformin", "strength": "500mg", "quantity": 200, "expiry_date": _ts_to_iso(now + timedelta(days=365)), "batch_number": "BTX-20260715", "threshold": 20, "is_low_stock": False, "is_expiring_soon": False},

        # New Items (25 items) to reach 30 total
        {"id": "INV-006", "drug_name": "Ibuprofen", "strength": "400mg", "quantity": 50, "expiry_date": _ts_to_iso(now + timedelta(days=200)), "batch_number": "BTX-20260505", "threshold": 15, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-007", "drug_name": "Omeprazole", "strength": "20mg", "quantity": 30, "expiry_date": _ts_to_iso(now + timedelta(days=120)), "batch_number": "BTX-20260214", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-008", "drug_name": "Azithromycin", "strength": "500mg", "quantity": 10, "expiry_date": _ts_to_iso(now + timedelta(days=40)), "batch_number": "BTX-20250920", "threshold": 5, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-009", "drug_name": "Amlodipine", "strength": "5mg", "quantity": 80, "expiry_date": _ts_to_iso(now + timedelta(days=300)), "batch_number": "BTX-20260810", "threshold": 20, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-010", "drug_name": "Atorvastatin", "strength": "10mg", "quantity": 60, "expiry_date": _ts_to_iso(now + timedelta(days=250)), "batch_number": "BTX-20260901", "threshold": 15, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-011", "drug_name": "Losartan", "strength": "50mg", "quantity": 100, "expiry_date": _ts_to_iso(now + timedelta(days=330)), "batch_number": "BTX-20261022", "threshold": 20, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-012", "drug_name": "Gabapentin", "strength": "300mg", "quantity": 7, "expiry_date": _ts_to_iso(now + timedelta(days=25)), "batch_number": "BTX-20250915", "threshold": 10, "is_low_stock": True, "is_expiring_soon": True},
        {"id": "INV-013", "drug_name": "Hydrochlorothiazide", "strength": "25mg", "quantity": 90, "expiry_date": _ts_to_iso(now + timedelta(days=280)), "batch_number": "BTX-20261111", "threshold": 20, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-014", "drug_name": "Sertraline", "strength": "50mg", "quantity": 40, "expiry_date": _ts_to_iso(now + timedelta(days=150)), "batch_number": "BTX-20260404", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-015", "drug_name": "Simvastatin", "strength": "20mg", "quantity": 55, "expiry_date": _ts_to_iso(now + timedelta(days=190)), "batch_number": "BTX-20260318", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-016", "drug_name": "Levothyroxine", "strength": "100mcg", "quantity": 25, "expiry_date": _ts_to_iso(now + timedelta(days=110)), "batch_number": "BTX-20260120", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-017", "drug_name": "Metoprolol", "strength": "50mg", "quantity": 35, "expiry_date": _ts_to_iso(now + timedelta(days=140)), "batch_number": "BTX-20260228", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-018", "drug_name": "Albuterol Inhaler", "strength": "90mcg", "quantity": 12, "expiry_date": _ts_to_iso(now + timedelta(days=360)), "batch_number": "BTX-20260606", "threshold": 5, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-019", "drug_name": "Escitalopram", "strength": "10mg", "quantity": 4, "expiry_date": _ts_to_iso(now + timedelta(days=45)), "batch_number": "BTX-20251010", "threshold": 10, "is_low_stock": True, "is_expiring_soon": False},
        {"id": "INV-020", "drug_name": "Prednisone", "strength": "20mg", "quantity": 20, "expiry_date": _ts_to_iso(now + timedelta(days=80)), "batch_number": "BTX-20251122", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-021", "drug_name": "Ciprofloxacn", "strength": "500mg", "quantity": 15, "expiry_date": _ts_to_iso(now + timedelta(days=70)), "batch_number": "BTX-20251105", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-022", "drug_name": "Doxycycline", "strength": "100mg", "quantity": 6, "expiry_date": _ts_to_iso(now + timedelta(days=12)), "batch_number": "BTX-20250815", "threshold": 8, "is_low_stock": True, "is_expiring_soon": True},
        {"id": "INV-023", "drug_name": "Insulin Glargine", "strength": "100U/ml", "quantity": 10, "expiry_date": _ts_to_iso(now + timedelta(days=60)), "batch_number": "BTX-20251201", "threshold": 5, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-024", "drug_name": "Furosemide", "strength": "40mg", "quantity": 28, "expiry_date": _ts_to_iso(now + timedelta(days=100)), "batch_number": "BTX-20251215", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-025", "drug_name": "Clopidogrel", "strength": "75mg", "quantity": 42, "expiry_date": _ts_to_iso(now + timedelta(days=310)), "batch_number": "BTX-20260909", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-026", "drug_name": "Montelukast", "strength": "10mg", "quantity": 65, "expiry_date": _ts_to_iso(now + timedelta(days=220)), "batch_number": "BTX-20260520", "threshold": 15, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-027", "drug_name": "Aspirin", "strength": "81mg", "quantity": 150, "expiry_date": _ts_to_iso(now + timedelta(days=400)), "batch_number": "BTX-20261201", "threshold": 30, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-028", "drug_name": "Diazepam", "strength": "5mg", "quantity": 18, "expiry_date": _ts_to_iso(now + timedelta(days=95)), "batch_number": "BTX-20251220", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False},
        {"id": "INV-029", "drug_name": "Tramadol", "strength": "50mg", "quantity": 5, "expiry_date": _ts_to_iso(now + timedelta(days=18)), "batch_number": "BTX-20250810", "threshold": 10, "is_low_stock": True, "is_expiring_soon": True},
        {"id": "INV-030", "drug_name": "Warfarin", "strength": "5mg", "quantity": 33, "expiry_date": _ts_to_iso(now + timedelta(days=160)), "batch_number": "BTX-20260305", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False}
    ]
    # sorted soonest-expiry first (already ordered above somewhat)
    seed.sort(key=lambda x: x["expiry_date"])
    return seed


def _mock_update_stock(item_id: str, new_quantity: int) -> dict:
    print(f"[MOCK] Inventory {item_id} quantity → {new_quantity}")
    return {
        "id": item_id,
        "drug_name": "Paracetamol",
        "strength": "650mg",
        "quantity": new_quantity,
        "expiry_date": _ts_to_iso(_now() + timedelta(days=90)),
        "batch_number": "BTX-20251210",
        "threshold": 10,
        "is_low_stock": new_quantity < 10,
        "is_expiring_soon": False,
    }


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
    
    return enriched


def _mock_delete_item(item_id: str) -> bool:
    print(f"[MOCK] Deleted Inventory {item_id}")
    return True
