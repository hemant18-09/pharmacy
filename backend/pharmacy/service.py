"""
Pharmacy Service – Firestore query helpers and business logic.

Uses the project-wide FirebaseService singleton but adds
pharmacy-specific operations (stats aggregation, status transitions,
notification triggers).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.core.firebase import firebase_service
from pharmacy.models import (
    DeliveryMode,
    DoctorInfo,
    MedicationItem,
    OrderTimestamps,
    PatientInfo,
    PharmacyOrder,
    PrescriptionStatus,
)

# Firestore collection names
ORDERS_COLLECTION = "pharmacy_orders"
INVENTORY_COLLECTION = "pharmacy_inventory"

# ──────────────────────────────────────────────
# Status → UI chip colour mapping (used by the list endpoint)
# ──────────────────────────────────────────────
STATUS_COLOR_MAP: Dict[str, str] = {
    PrescriptionStatus.NEW: "teal",
    PrescriptionStatus.ACCEPTED: "blue",
    PrescriptionStatus.PREPARING: "amber",
    PrescriptionStatus.READY: "green",
    PrescriptionStatus.DELIVERED: "green",
    PrescriptionStatus.PICKED_UP: "gray",
    PrescriptionStatus.REJECTED: "red",
}


def _now() -> datetime:
    return datetime.utcnow()


def _start_of_today() -> datetime:
    now = _now()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _ts_to_iso(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    # If it's already a string (Firestore sometimes returns strings for Timestamps if not converted), return as is
    if isinstance(dt, str):
        return dt
    if dt.tzinfo is None:
        # Assume UTC if naive
        return dt.isoformat() + "Z"
    return dt.isoformat()


# ──────────────────────────────────────────────
# 1.  Dashboard Stats
# ──────────────────────────────────────────────


# ──────────────────────────────────────────────
# 1.a  Pharmacy Listing (for Patient Portal)
# ──────────────────────────────────────────────

async def list_pharmacies(lat: Optional[float] = None, lng: Optional[float] = None) -> List[dict]:
    """
    Returns a list of verified pharmacies for the patient to choose from.
    If lat/lng provided, could sort by distance (simple implementation for now).
    """
    if firebase_service.mock_mode:
        return _mock_pharmacy_list()

    db = firebase_service.db
    # Filter only verified pharmacies
    docs = db.collection("pharmacies").where("is_verified", "==", True).stream()
    
    results = []
    for doc in docs:
        d = doc.to_dict()
        results.append({
            "id": doc.id,
            "name": d.get("name", "Unknown Pharmacy"),
            "location": d.get("location", {}),
            "is_verified": d.get("is_verified", False),
            "rating": d.get("rating", 0.0)
        })
    
    return results

def _mock_pharmacy_list():
    return [
        {"id": "mock-p1", "name": "Apollo Mock", "location": {"address": "Delhi"}, "is_verified": True, "rating": 4.5},
        {"id": "mock-p2", "name": "MedPlus Mock", "location": {"address": "Noida"}, "is_verified": True, "rating": 4.2}
    ]


async def get_dashboard_stats() -> dict:
    """
    Returns the 4 metric cards for the pharmacy dashboard.
    Falls back to mock data when Firebase is in mock mode.
    """
    if firebase_service.mock_mode:
        return _mock_dashboard_stats()

    db = firebase_service.db
    today_start = _start_of_today()

    # -- New prescriptions today --
    new_today_q = (
        db.collection(ORDERS_COLLECTION)
        .where("status", "==", PrescriptionStatus.NEW)
        .where("timestamps.created_at", ">=", today_start)
        .stream()
    )
    new_prescriptions_today = sum(1 for _ in new_today_q)

    # -- In-progress (ACCEPTED + PREPARING) --
    in_progress_statuses = [PrescriptionStatus.ACCEPTED, PrescriptionStatus.PREPARING]
    in_progress_count = 0
    for s in in_progress_statuses:
        docs = db.collection(ORDERS_COLLECTION).where("status", "==", s).stream()
        in_progress_count += sum(1 for _ in docs)

    # -- Delivered / picked-up today --
    completed_count = 0
    for s in [PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP]:
        docs = (
            db.collection(ORDERS_COLLECTION)
            .where("status", "==", s)
            .where("timestamps.completed_at", ">=", today_start)
            .stream()
        )
        completed_count += sum(1 for _ in docs)

    # -- Low stock alerts --
    low_stock_count = 0
    try:
        inv_docs = db.collection(INVENTORY_COLLECTION).stream()
        for doc in inv_docs:
            d = doc.to_dict()
            if d.get("quantity", 0) < d.get("threshold", 10):
                low_stock_count += 1
    except Exception:
        low_stock_count = 0

    return {
        "new_prescriptions_today": new_prescriptions_today,
        "orders_in_progress": in_progress_count,
        "orders_delivered_today": completed_count,
        "low_stock_alerts": low_stock_count,
    }


def _mock_dashboard_stats() -> dict:
    """Deterministic mock data so the frontend always has something to render."""
    today = _start_of_today()
    
    # Import mock inventory from inventory service to check low stock
    try:
        from pharmacy.inventory_service import _MOCK_INVENTORY_DB
        low_stock_count = sum(1 for item in _MOCK_INVENTORY_DB if item.get("is_low_stock", False))
    except ImportError:
        low_stock_count = 2 # Fallback
        
    new_prescriptions_today = 0
    orders_in_progress = 0
    orders_delivered_today = 0
    
    for order in _MOCK_ORDERS_DB:
        status = order.get("status")
        created_at_str = order.get("timestamps", {}).get("created_at")
        completed_at_str = order.get("timestamps", {}).get("completed_at")
        
        # Parse dates (naive/simple check)
        created_at = None
        if created_at_str:
             try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                if created_at.tzinfo: created_at = created_at.replace(tzinfo=None) # Compare naive
             except: pass
             
        completed_at = None
        if completed_at_str:
            try:
                completed_at = datetime.fromisoformat(completed_at_str.replace("Z", "+00:00"))
                if completed_at.tzinfo: completed_at = completed_at.replace(tzinfo=None)
            except: pass

        # New Today
        if status == PrescriptionStatus.NEW:
            if created_at and created_at >= today:
                new_prescriptions_today += 1
                
        # In Progress
        if status in [PrescriptionStatus.ACCEPTED, PrescriptionStatus.PREPARING]:
            orders_in_progress += 1
            
        # Delivered Today
        if status in [PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP]:
            if completed_at and completed_at >= today:
                orders_delivered_today += 1

    return {
        "new_prescriptions_today": new_prescriptions_today,
        "orders_in_progress": orders_in_progress,
        "orders_delivered_today": orders_delivered_today,
        "low_stock_alerts": low_stock_count,
    }


# ──────────────────────────────────────────────
# 2.  Order Listing  (with status / date filter)
# ──────────────────────────────────────────────

# ──────────────────────────────────────────────
# 2.  Order Listing  (with status / date filter)
# ──────────────────────────────────────────────

async def list_orders(
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> List[dict]:
    """
    Returns lightweight order summaries for the sidebar / table.
    Each item includes a `color_code` matching the UI chip.
    """
    if firebase_service.mock_mode:
        return _mock_order_list(status)

    db = firebase_service.db
    query = db.collection(ORDERS_COLLECTION)

    if status:
        query = query.where("status", "==", status)
    if date_from:
        query = query.where("timestamps.created_at", ">=", date_from)
    if date_to:
        query = query.where("timestamps.created_at", "<=", date_to)

    query = query.order_by("timestamps.created_at", direction="DESCENDING")
    docs = query.stream()

    results: List[dict] = []
    for doc in docs:
        d = doc.to_dict()
        s = d.get("status", PrescriptionStatus.NEW)
        ts = d.get("timestamps", {})
        results.append(
            {
                "id": doc.id,
                "patient_name": d.get("patient_info", {}).get("name", "—"),
                "status": s,
                "color_code": STATUS_COLOR_MAP.get(s, "gray"),
                "medication_count": len(d.get("medications", [])),
                "created_at": _ts_to_iso(ts.get("created_at")),
                "accepted_at": _ts_to_iso(ts.get("accepted_at")),
                "ready_at": _ts_to_iso(ts.get("ready_at")),
                "completed_at": _ts_to_iso(ts.get("completed_at")),
            }
        )
    return results

# ──────────────────────────────────────────────
# Mock In-Memory DB (Global State)
# ──────────────────────────────────────────────

from pharmacy.mock_data import get_initial_mock_orders

# Initialize mock DB with fresh data on module load
_MOCK_ORDERS_DB = get_initial_mock_orders()

def _mock_order_list(status_filter: Optional[str] = None) -> List[dict]:
    """Seed data for local development."""
    # Add color codes dynamically if not present
    results = []
    for o in _MOCK_ORDERS_DB:
        # Shallow copy to avoid mutating global state unnecessarily in read operations
        order = o.copy()
        order["color_code"] = STATUS_COLOR_MAP.get(order["status"], "gray") 
        # Calculate medication count if not present
        if "medication_count" not in order:
            order["medication_count"] = len(order.get("medications", []))
        
        # Flatten patient name for list view
        if "patient_name" not in order:
             order["patient_name"] = order.get("patient_info", {}).get("name", "Unknown")

        if status_filter:
            if order["status"] == status_filter:
                results.append(order)
        else:
            results.append(order)
            
    # Sort by created_at desc
    results.sort(key=lambda x: x["timestamps"]["created_at"] or "", reverse=True)
    return results


# ──────────────────────────────────────────────
# 3.  Order Detail
# ──────────────────────────────────────────────

async def get_order_detail(order_id: str) -> Optional[dict]:
    """Full order document with patient & doctor cards."""
    if firebase_service.mock_mode:
        return _mock_order_detail(order_id)

    db = firebase_service.db
    doc = db.collection(ORDERS_COLLECTION).document(order_id).get()
    if not doc.exists:
        return None

    d = doc.to_dict()
    ts = d.get("timestamps", {})
    pi = d.get("patient_info", {})
    di = d.get("doctor_info", {})

    return {
        "id": doc.id,
        "patient_name": pi.get("name"),
        "patient_age": pi.get("age"),
        "patient_gender": pi.get("gender"),
        "patient_contact_id": pi.get("contact_id"),
        "doctor_name": di.get("name"),
        "doctor_registration_id": di.get("registration_id"),
        "medications": d.get("medications", []),
        "status": d.get("status", PrescriptionStatus.NEW),
        "color_code": STATUS_COLOR_MAP.get(d.get("status", PrescriptionStatus.NEW), "gray"),
        "delivery_mode": d.get("delivery_mode", DeliveryMode.STORE_PICKUP),
        "created_at": _ts_to_iso(ts.get("created_at")),
        "accepted_at": _ts_to_iso(ts.get("accepted_at")),
        "ready_at": _ts_to_iso(ts.get("ready_at")),
        "completed_at": _ts_to_iso(ts.get("completed_at")),
    }


def _mock_order_detail(order_id: str) -> Optional[dict]:
    for order in _MOCK_ORDERS_DB:
        if order["id"] == order_id:
            # Flatten structure to match response schema
            d = order.copy()
            pi = d.get("patient_info", {})
            di = d.get("doctor_info", {})
            ts = d.get("timestamps", {})
            
            return {
                "id": d["id"],
                "patient_name": pi.get("name"),
                "patient_age": pi.get("age"),
                "patient_gender": pi.get("gender"),
                "patient_contact_id": pi.get("contact_id"),
                "doctor_name": di.get("name"),
                "doctor_registration_id": di.get("registration_id"),
                "medications": d.get("medications", []),
                "status": d.get("status"),
                "color_code": STATUS_COLOR_MAP.get(d.get("status"), "gray"),
                "delivery_mode": d.get("delivery_mode", DeliveryMode.STORE_PICKUP),
                "created_at": ts.get("created_at"),
                "accepted_at": ts.get("accepted_at"),
                "ready_at": ts.get("ready_at"),
                "completed_at": ts.get("completed_at"),
            }
    return None


# ──────────────────────────────────────────────
# 4.  Status Transition + Side-effects
# ──────────────────────────────────────────────

async def update_order_status(order_id: str, new_status: str) -> dict:
    """
    Advance an order's status.
    Side-effects:
      - READY   → trigger patient notification
      - DELIVERED / PICKED_UP → stamp completed_at
    """
    if firebase_service.mock_mode:
        return _mock_status_update(order_id, new_status)

    db = firebase_service.db
    doc_ref = db.collection(ORDERS_COLLECTION).document(order_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None

    update_payload: dict = {"status": new_status}
    now = _now()

    if new_status == PrescriptionStatus.ACCEPTED:
        update_payload["timestamps.accepted_at"] = now

    if new_status == PrescriptionStatus.READY:
        update_payload["timestamps.ready_at"] = now
        _notify_patient_ready(doc.to_dict())

    if new_status in (PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP):
        update_payload["timestamps.completed_at"] = now

    doc_ref.update(update_payload)

    return {
        "id": order_id,
        "status": new_status,
        "color_code": STATUS_COLOR_MAP.get(new_status, "gray"),
        "updated_at": _ts_to_iso(now),
    }


def _mock_status_update(order_id: str, new_status: str) -> Optional[dict]:
    print(f"[MOCK] Order {order_id} → {new_status}")
    
    # Update global mock DB
    for order in _MOCK_ORDERS_DB:
        if order["id"] == order_id:
            order["status"] = new_status
            ts = order["timestamps"]
            now_iso = _ts_to_iso(_now())
            
            if new_status == PrescriptionStatus.ACCEPTED:
                ts["accepted_at"] = now_iso
            elif new_status == PrescriptionStatus.READY:
                ts["ready_at"] = now_iso
            elif new_status in (PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP):
                ts["completed_at"] = now_iso
                
            return {
                "id": order_id,
                "status": new_status,
                "color_code": STATUS_COLOR_MAP.get(new_status, "gray"),
                "updated_at": now_iso,
            }
    return None


# ──────────────────────────────────────────────
# 5.  Create Order  (called by agent or doctor flow)
# ──────────────────────────────────────────────

async def create_order(
    patient_name: str,
    patient_age: int,
    patient_gender: str,
    patient_contact_id: str,
    doctor_name: str,
    doctor_registration_id: str,
    medications: List[dict],
    delivery_mode: str = DeliveryMode.STORE_PICKUP,
) -> dict:
    """Persist a new PharmacyOrder and return the created document."""
    order_id = f"RX-{uuid.uuid4().hex[:8].upper()}"
    now = _now()

    order_data = {
        "id": order_id, # Added ID here for consistency
        "patient_info": {
            "name": patient_name,
            "age": patient_age,
            "gender": patient_gender,
            "contact_id": patient_contact_id,
        },
        "doctor_info": {
            "name": doctor_name,
            "registration_id": doctor_registration_id,
        },
        "medications": medications,
        "status": PrescriptionStatus.NEW,
        "delivery_mode": delivery_mode,
        "timestamps": {
            "created_at": _ts_to_iso(now),
            "accepted_at": None,
            "ready_at": None,
            "completed_at": None,
        },
    }

    if firebase_service.mock_mode:
        print(f"[MOCK] Created pharmacy order {order_id}")
        _MOCK_ORDERS_DB.insert(0, order_data) # Add to mock DB
        return order_data

    db = firebase_service.db
    # Remove 'id' if you don't want it stored in the doc body, but it's often useful
    store_data = order_data.copy() 
    store_data.pop("id")
    # Convert string timestamps back to datetime for Firestore if needed, 
    # but for now reusing the logic as is.
    store_data["timestamps"]["created_at"] = now 
    
    db.collection(ORDERS_COLLECTION).document(order_id).set(store_data)
    return order_data


# ──────────────────────────────────────────────
# Notification helpers (placeholder – plug in FCM / SMS)
# ──────────────────────────────────────────────

def _notify_patient_ready(order_data: dict) -> None:
    """
    Fire a push / SMS notification to the patient that their
    prescription is ready for pickup / delivery.
    Currently logs; replace with FCM / Twilio in production.
    """
    patient = order_data.get("patient_info", {})
    name = patient.get("name", "Patient")
    contact = patient.get("contact_id", "N/A")
    print(f"[NOTIFICATION] 📦 Prescription READY for {name} (contact: {contact})")
