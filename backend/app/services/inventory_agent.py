from typing import List, Tuple

async def validate_stock_for_order(order_id: str) -> Tuple[bool, List[dict]]:
    # Mock implementation: always valid
    return True, []

async def decrement_stock_for_order(order_id: str) -> dict:
    # Mock implementation
    return {"decremented_count": 0, "decremented": [], "errors": []}

async def cleanup_expiring_inventory() -> dict:
    # Mock implementation
    return {
        "status": "success",
        "restricted_count": 0,
        "already_restricted": 0,
        "restricted_items": [],
        "scanned_at": "2024-01-01T00:00:00Z"
    }

async def get_inventory_health() -> dict:
    # Mock implementation
    return {
        "total_items": 100,
        "total_units": 500,
        "low_stock_count": 5,
        "expiring_soon_count": 2,
        "restricted_count": 0,
        "health_score": 95.0,
        "checked_at": "2024-01-01T00:00:00Z"
    }
