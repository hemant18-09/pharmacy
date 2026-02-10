"""
Chat Service – Secure messaging between pharmacist and patient.

Security rules:
  • Messages can only be sent for orders that exist AND are NOT completed
    (i.e. status is NOT DELIVERED / PICKED_UP).
  • Once an order reaches DELIVERED or PICKED_UP the chat is read-only.

Firestore layout:
  pharmacy_chats/{order_id}/messages/{msg_id}
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from app.core.firebase import firebase_service
from pharmacy.models import PrescriptionStatus

ORDERS_COLLECTION = "pharmacy_orders"
CHATS_COLLECTION = "pharmacy_chats"

# Statuses that lock the chat (order is terminal)
_LOCKED_STATUSES = {PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP}


def _now() -> datetime:
    return datetime.utcnow()


def _ts_to_iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() + "Z" if dt else None


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

async def _get_order_status(order_id: str) -> Optional[str]:
    """Return the current status string for an order, or None if not found."""
    if firebase_service.mock_mode:
        # In mock mode pretend all orders exist and are active
        # except a hard-coded "completed" order for testing
        if order_id == "RX-LOCKED":
            return PrescriptionStatus.DELIVERED
        return PrescriptionStatus.PREPARING

    db = firebase_service.db
    doc = db.collection(ORDERS_COLLECTION).document(order_id).get()
    if not doc.exists:
        return None
    return doc.to_dict().get("status")


def _is_chat_locked(status: str) -> bool:
    return status in _LOCKED_STATUSES


# ──────────────────────────────────────────────
# 1. Send message
# ──────────────────────────────────────────────

async def send_message(
    order_id: str,
    sender: str,
    message: str,
    category: str = "general",
) -> Tuple[Optional[dict], Optional[str]]:
    """
    Returns (message_dict, error_string).
    error_string is set when validation fails.
    """
    # --- Validate order exists ---
    status = await _get_order_status(order_id)
    if status is None:
        return None, f"Order {order_id} not found"

    # --- Security: chat locked? ---
    if _is_chat_locked(status):
        return None, (
            f"Chat for order {order_id} is locked (status: {status}). "
            "No new messages allowed after delivery / pickup."
        )

    msg_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
    now = _now()

    msg_data = {
        "id": msg_id,
        "order_id": order_id,
        "sender": sender,
        "message": message,
        "category": category,
        "created_at": _ts_to_iso(now),
    }

    if firebase_service.mock_mode:
        print(f"[MOCK CHAT] {sender} → order {order_id}: {message[:40]}…")
        return msg_data, None

    db = firebase_service.db
    db.collection(CHATS_COLLECTION).document(order_id) \
        .collection("messages").document(msg_id).set({
            **msg_data,
            "created_at": now,  # store as Firestore Timestamp
        })
    return msg_data, None


# ──────────────────────────────────────────────
# 2. Get chat history
# ──────────────────────────────────────────────

async def get_chat_history(order_id: str) -> Tuple[Optional[List[dict]], bool, Optional[str]]:
    """
    Returns (messages_list, is_locked, error_string).
    `is_locked` tells the frontend to disable the input box.
    """
    status = await _get_order_status(order_id)
    if status is None:
        return None, False, f"Order {order_id} not found"

    locked = _is_chat_locked(status)

    if firebase_service.mock_mode:
        return _mock_chat_history(order_id), locked, None

    db = firebase_service.db
    docs = (
        db.collection(CHATS_COLLECTION).document(order_id)
        .collection("messages")
        .order_by("created_at")
        .stream()
    )
    messages = []
    for doc in docs:
        d = doc.to_dict()
        ts = d.get("created_at")
        messages.append({
            "id": doc.id,
            "order_id": order_id,
            "sender": d.get("sender"),
            "message": d.get("message"),
            "category": d.get("category", "general"),
            "created_at": _ts_to_iso(ts) if isinstance(ts, datetime) else str(ts),
        })
    return messages, locked, None


# ──────────────────────────────────────────────
# Mock data
# ──────────────────────────────────────────────

def _mock_chat_history(order_id: str) -> List[dict]:
    now = _now()
    return [
        {
            "id": "MSG-A1",
            "order_id": order_id,
            "sender": "PHARMACIST",
            "message": "Hi, your prescription is being prepared. Paracetamol 650mg is temporarily out of stock — we'll substitute with Dolo-650. Is that okay?",
            "category": "availability",
            "created_at": _ts_to_iso(now - timedelta(minutes=45)),
        },
        {
            "id": "MSG-A2",
            "order_id": order_id,
            "sender": "PATIENT",
            "message": "Yes, Dolo-650 is fine. When will it be ready?",
            "category": "availability",
            "created_at": _ts_to_iso(now - timedelta(minutes=40)),
        },
        {
            "id": "MSG-A3",
            "order_id": order_id,
            "sender": "PHARMACIST",
            "message": "Should be ready in about 20 minutes. We'll notify you!",
            "category": "delivery",
            "created_at": _ts_to_iso(now - timedelta(minutes=38)),
        },
    ]
