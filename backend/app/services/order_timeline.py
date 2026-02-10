from typing import List, Optional

async def log_status_change(order_id: str, old_status: str, new_status: str, actor_id: str) -> None:
    # Mock implementation
    print(f"[MOCK] Logged status change for {order_id}: {old_status} -> {new_status} by {actor_id}")

async def log_stock_sync(order_id: str, decrement_count: int) -> None:
    # Mock implementation
    print(f"[MOCK] Logged stock sync for {order_id}: -{decrement_count}")

async def log_prescription_verification(order_id: str, is_valid: bool, doctor_id: str) -> None:
    # Mock implementation
    print(f"[MOCK] Logged verification for {order_id}: Valid={is_valid}")

async def log_event(order_id: str, event_type: str, description: str, metadata: dict = None) -> None:
    # Mock implementation
    print(f"[MOCK] Logged event for {order_id}: {event_type} - {description}")

async def get_order_timeline(order_id: str) -> List[dict]:
    # Mock implementation
    return [
        {
            "id": "evt_1",
            "event_type": "ORDER_CREATED",
            "description": "Order received from Dr. Smith",
            "timestamp": "2024-01-01T10:00:00Z",
            "actor_id": "SYSTEM",
            "metadata": {}
        }
    ]
