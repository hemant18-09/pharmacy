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
    return {
        "new_prescriptions_today": 4,
        "orders_in_progress": 7,
        "orders_delivered_today": 12,
        "low_stock_alerts": 2,
    }


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

_MOCK_ORDERS_DB = [
    { "id": "RX-1001", "patient_name": "Aarav Sharma", "status": PrescriptionStatus.NEW, "color_code": "teal", "medication_count": 3, "created_at": _ts_to_iso(_now() - timedelta(hours=1)), "accepted_at": None, "ready_at": None, "completed_at": None },
    { "id": "RX-1002", "patient_name": "Priya Patel", "status": PrescriptionStatus.ACCEPTED, "color_code": "blue", "medication_count": 2, "created_at": _ts_to_iso(_now() - timedelta(hours=3)), "accepted_at": _ts_to_iso(_now() - timedelta(hours=2, minutes=30)), "ready_at": None, "completed_at": None },
    { "id": "RX-1003", "patient_name": "Rohan Gupta", "status": PrescriptionStatus.PREPARING, "color_code": "amber", "medication_count": 5, "created_at": _ts_to_iso(_now() - timedelta(hours=5)), "accepted_at": _ts_to_iso(_now() - timedelta(hours=4, minutes=30)), "ready_at": None, "completed_at": None },
    { "id": "RX-1004", "patient_name": "Sneha Reddy", "status": PrescriptionStatus.READY, "color_code": "green", "medication_count": 1, "created_at": _ts_to_iso(_now() - timedelta(hours=8)), "accepted_at": _ts_to_iso(_now() - timedelta(hours=7, minutes=30)), "ready_at": _ts_to_iso(_now() - timedelta(hours=6)), "completed_at": None },
    { "id": "RX-1005", "patient_name": "Vikram Singh", "status": PrescriptionStatus.DELIVERED, "color_code": "green", "medication_count": 4, "created_at": _ts_to_iso(_now() - timedelta(hours=12)), "accepted_at": _ts_to_iso(_now() - timedelta(hours=11, minutes=30)), "ready_at": _ts_to_iso(_now() - timedelta(hours=10)), "completed_at": _ts_to_iso(_now() - timedelta(hours=9)) },
    { "id": "RX-1006", "patient_name": "Anita Desai", "status": PrescriptionStatus.NEW, "color_code": "teal", "medication_count": 2, "created_at": _ts_to_iso(_now() - timedelta(minutes=30)), "accepted_at": None, "ready_at": None, "completed_at": None },
    { "id": "RX-1011", "patient_name": "Karan Mehta", "status": PrescriptionStatus.NEW, "color_code": "teal", "medication_count": 1, "created_at": _ts_to_iso(_now() - timedelta(minutes=20)), "accepted_at": None, "ready_at": None, "completed_at": None },
    { "id": "RX-1012", "patient_name": "Nisha Kapoor", "status": PrescriptionStatus.NEW, "color_code": "teal", "medication_count": 4, "created_at": _ts_to_iso(_now() - timedelta(minutes=15)), "accepted_at": None, "ready_at": None, "completed_at": None },
    { "id": "RX-1013", "patient_name": "Dev Malhotra", "status": PrescriptionStatus.NEW, "color_code": "teal", "medication_count": 2, "created_at": _ts_to_iso(_now() - timedelta(minutes=10)), "accepted_at": None, "ready_at": None, "completed_at": None },
    { "id": "RX-1014", "patient_name": "Riya Shah", "status": PrescriptionStatus.NEW, "color_code": "teal", "medication_count": 3, "created_at": _ts_to_iso(_now() - timedelta(minutes=5)), "accepted_at": None, "ready_at": None, "completed_at": None },
    { "id": "RX-1007", "patient_name": "Rahul Verma", "status": PrescriptionStatus.REJECTED, "color_code": "red", "medication_count": 1, "created_at": _ts_to_iso(_now() - timedelta(days=1)), "accepted_at": None, "ready_at": None, "completed_at": None },
    { "id": "RX-1008", "patient_name": "Kavita Kapoor", "status": PrescriptionStatus.PICKED_UP, "color_code": "gray", "medication_count": 3, "created_at": _ts_to_iso(_now() - timedelta(days=2)), "accepted_at": _ts_to_iso(_now() - timedelta(days=2, hours=1)), "ready_at": _ts_to_iso(_now() - timedelta(days=2, hours=2)), "completed_at": _ts_to_iso(_now() - timedelta(days=2, hours=3)) },
    { "id": "RX-1009", "patient_name": "Amit Shah", "status": PrescriptionStatus.ACCEPTED, "color_code": "blue", "medication_count": 6, "created_at": _ts_to_iso(_now() - timedelta(hours=2)), "accepted_at": _ts_to_iso(_now() - timedelta(hours=1, minutes=30)), "ready_at": None, "completed_at": None },
    { "id": "RX-1010", "patient_name": "Neha Joshi", "status": PrescriptionStatus.PREPARING, "color_code": "amber", "medication_count": 2, "created_at": _ts_to_iso(_now() - timedelta(hours=4)), "accepted_at": _ts_to_iso(_now() - timedelta(hours=3, minutes=30)), "ready_at": None, "completed_at": None },
]

def _mock_order_list(status_filter: Optional[str] = None) -> List[dict]:
    """Seed data for local development."""
    if status_filter:
        return [o for o in _MOCK_ORDERS_DB if o["status"] == status_filter]
    return _MOCK_ORDERS_DB


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


def _mock_order_detail(order_id: str) -> dict:
    return {
        "id": order_id,
        "patient_name": "Aarav Sharma",
        "patient_age": 34,
        "patient_gender": "Male",
        "patient_contact_id": "PAT-9001",
        "doctor_name": "Dr. Meena Iyer",
        "doctor_registration_id": "MCI-78432",
        "medications": [
            {"drug_name": "Amoxicillin", "strength": "500mg", "frequency": "1-0-1", "duration": "5 Days", "instructions": "After food"},
            {"drug_name": "Paracetamol", "strength": "650mg", "frequency": "1-1-1", "duration": "3 Days", "instructions": "As needed"},
            {"drug_name": "Pantoprazole", "strength": "40mg", "frequency": "1-0-0", "duration": "5 Days", "instructions": "Before breakfast"},
        ],
        "status": PrescriptionStatus.NEW,
        "color_code": "teal",
        "delivery_mode": DeliveryMode.STORE_PICKUP,
        "created_at": _ts_to_iso(_now() - timedelta(hours=1)),
        "accepted_at": None,
        "ready_at": None,
        "completed_at": None,
    }


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


def _mock_status_update(order_id: str, new_status: str) -> dict:
    print(f"[MOCK] Order {order_id} → {new_status}")
    
    # Update global mock DB
    for order in _MOCK_ORDERS_DB:
        if order["id"] == order_id:
            order["status"] = new_status
            order["color_code"] = STATUS_COLOR_MAP.get(new_status, "gray")
            now = _now()
            if new_status == PrescriptionStatus.ACCEPTED:
                order["accepted_at"] = _ts_to_iso(now)
            if new_status == PrescriptionStatus.READY:
                order["ready_at"] = _ts_to_iso(now)
            if new_status in (PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP):
                order["completed_at"] = _ts_to_iso(now)
            break
            
    return {
        "id": order_id,
        "status": new_status,
        "color_code": STATUS_COLOR_MAP.get(new_status, "gray"),
        "updated_at": _ts_to_iso(_now()),
    }


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
            "created_at": now,
            "accepted_at": None,
            "ready_at": None,
            "completed_at": None,
        },
    }

    if firebase_service.mock_mode:
        print(f"[MOCK] Created pharmacy order {order_id}")
        return {"id": order_id, **order_data, "timestamps": {k: _ts_to_iso(v) for k, v in order_data["timestamps"].items()}}

    db = firebase_service.db
    db.collection(ORDERS_COLLECTION).document(order_id).set(order_data)
    return {"id": order_id, **order_data}


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
