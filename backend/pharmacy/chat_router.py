"""
FastAPI Router – Pharmacy Secure Messaging
Prefix: /pharmacy/chat

Security:
  • POST is blocked when order status is DELIVERED or PICKED_UP (chat locked).
  • GET returns an `is_locked` flag so the frontend can disable the input box.

Endpoints:
  POST /pharmacy/chat/send                → Send a message on an active order
  GET  /pharmacy/chat/{order_id}/history   → Retrieve conversation log
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from pharmacy.schemas import (
    ChatHistoryResponse,
    ChatMessageResponse,
    SendMessageRequest,
)
from pharmacy import chat_service as svc

router = APIRouter(prefix="/pharmacy/chat", tags=["Pharmacy Chat"])


# ──────────────────────────────────────────────
# 1. Send a message
# ──────────────────────────────────────────────

@router.post("/send", response_model=ChatMessageResponse)
async def send_message(body: SendMessageRequest):
    """
    Send a text message on an active order.

    Validates:
    1. `order_id` exists.
    2. Order is NOT in a terminal state (DELIVERED / PICKED_UP).

    Allowed categories: `delivery`, `availability`, `general`.
    """
    msg, error = await svc.send_message(
        order_id=body.order_id,
        sender=body.sender,
        message=body.message,
        category=body.category,
    )
    if error:
        status_code = 404 if "not found" in error else 403
        raise HTTPException(status_code=status_code, detail=error)
    return msg


# ──────────────────────────────────────────────
# 2. Chat history
# ──────────────────────────────────────────────

@router.get("/{order_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(order_id: str):
    """
    Retrieve all messages for an order.

    Response includes `is_locked: true` when the order is completed,
    signalling the frontend to render the chat as **read-only**.
    """
    messages, is_locked, error = await svc.get_chat_history(order_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return {
        "order_id": order_id,
        "is_locked": is_locked,
        "messages": messages,
    }
