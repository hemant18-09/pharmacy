"""
FastAPI Router – Pharmacy V2 (Advanced Agentic Features)
Prefix: /pharmacy/v2

This router extends the base pharmacy module with:
  1. Automated Inventory Sync (Stock Guardian)
  2. Prescription Verification (Hash & Sign)
  3. Order Timeline & Audit Log
  4. Batch Expiry Cleanup Agent
  5. Optimized Delivery Routes for Leaflet

All endpoints integrate with the existing NEW → ACCEPTED → PREPARING → READY
→ DELIVERED / PICKED_UP status flow.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from pharmacy.models import PrescriptionStatus, DeliveryMode
from pharmacy.schemas import (
    OrderDetailResponse,
    StatusUpdateResponse,
    UpdateOrderStatusRequest,
)
from pharmacy import service as order_service

# New V2 services
from app.services.inventory_agent import (
    validate_stock_for_order,
    decrement_stock_for_order,
    cleanup_expiring_inventory,
    get_inventory_health,
)
from app.services.prescription_verification import (
    generate_prescription_hash,
    verify_prescription,
    sign_order_payload,
)
from app.services.order_timeline import (
    get_order_timeline,
    log_status_change,
    log_stock_sync,
    log_prescription_verification,
    log_event,
)
from app.services.delivery_route import (
    get_delivery_route,
    get_batch_delivery_routes,
)


router = APIRouter(prefix="/pharmacy/v2", tags=["Pharmacy V2 – Agentic"])


# ══════════════════════════════════════════════
#  REQUEST / RESPONSE SCHEMAS (V2)
# ══════════════════════════════════════════════

class StockValidationResponse(BaseModel):
    is_valid: bool
    order_id: str
    missing_items: List[dict] = []
    message: str


class StockDecrementResponse(BaseModel):
    order_id: str
    decremented_count: int
    decremented: List[dict] = []
    errors: List[str] = []
    timestamp: Optional[str] = None


class PrescriptionVerifyRequest(BaseModel):
    order_id: str
    doctor_id: str
    medications: List[dict]
    created_at: str
    expected_hash: str


class PrescriptionVerifyResponse(BaseModel):
    is_valid: bool
    doctor_id: str
    medication_count: int
    computed_hash_prefix: str
    expected_hash_prefix: str
    verified_at: str
    verdict: str


class PrescriptionSignRequest(BaseModel):
    doctor_id: str
    medications: List[dict]
    created_at: str


class PrescriptionSignResponse(BaseModel):
    prescription_hash: str
    doctor_id: str
    medication_count: int
    signed_at: str


class TimelineEventResponse(BaseModel):
    id: str
    event_type: str
    description: str
    timestamp: Optional[str] = None
    actor_id: str = "SYSTEM"
    metadata: dict = {}


class ExpiryCleanupResponse(BaseModel):
    status: str
    restricted_count: int
    already_restricted: int
    restricted_items: List[dict] = []
    scanned_at: Optional[str] = None


class InventoryHealthResponse(BaseModel):
    total_items: int
    total_units: int
    low_stock_count: int
    expiring_soon_count: int
    restricted_count: int
    health_score: float
    checked_at: Optional[str] = None


class DeliveryRouteRequest(BaseModel):
    order_id: str
    delivery_address: Optional[dict] = None


class DeliveryRouteResponse(BaseModel):
    order_id: str
    route: dict
    delivery_status: str
    generated_at: str


class BatchRouteRequest(BaseModel):
    order_ids: List[str]


class AgenticStatusUpdateRequest(BaseModel):
    """Enhanced status update that triggers agentic side-effects."""
    status: PrescriptionStatus
    actor_id: str = Field(default="PHARMACIST", description="Who is performing this action")


# ══════════════════════════════════════════════
#  1. AGENTIC STATUS TRANSITION (with auto-sync)
# ══════════════════════════════════════════════

@router.patch(
    "/orders/{order_id}/status",
    response_model=StatusUpdateResponse,
    summary="Agentic Status Update with Auto-Sync",
)
async def agentic_status_update(
    order_id: str,
    body: AgenticStatusUpdateRequest,
    background_tasks: BackgroundTasks,
):
    """
    Advanced order status transition with agentic side-effects:

    - **NEW → ACCEPTED**: Validates stock availability, then auto-decrements inventory.
    - **ACCEPTED → PREPARING**: Logs stock sync confirmation in timeline.
    - **PREPARING → READY**: Notifies patient, logs timeline event.
    - **READY → DELIVERED/PICKED_UP**: Stamps completed_at, logs final event.

    Returns 400 if stock validation fails during ACCEPTED transition.
    """
    # Get current order status
    detail = await order_service.get_order_detail(order_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    old_status = detail["status"]
    new_status = body.status

    # ── ACCEPTED transition: validate + decrement stock ──
    if new_status in (PrescriptionStatus.ACCEPTED, PrescriptionStatus.PREPARING):
        is_valid, missing = await validate_stock_for_order(order_id)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INSUFFICIENT_STOCK",
                    "message": "Cannot accept order – some medications are out of stock.",
                    "missing_items": missing,
                },
            )

        # Auto-decrement in background
        if new_status == PrescriptionStatus.ACCEPTED:
            background_tasks.add_task(_run_stock_decrement, order_id)

    # Perform the actual status update
    result = await order_service.update_order_status(order_id, new_status)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    # Log timeline event in background
    background_tasks.add_task(
        log_status_change, order_id, old_status, new_status, body.actor_id
    )

    return result


async def _run_stock_decrement(order_id: str):
    """Background task to decrement stock and log it."""
    result = await decrement_stock_for_order(order_id)
    await log_stock_sync(order_id, result.get("decremented_count", 0))


# ══════════════════════════════════════════════
#  2. STOCK VALIDATION (standalone check)
# ══════════════════════════════════════════════

@router.get(
    "/orders/{order_id}/validate-stock",
    response_model=StockValidationResponse,
    summary="Validate Stock Availability",
)
async def validate_stock_endpoint(order_id: str):
    """
    Pre-check whether all medications in an order are available.
    Does NOT modify inventory – use the agentic status update for that.
    """
    is_valid, missing = await validate_stock_for_order(order_id)
    return StockValidationResponse(
        is_valid=is_valid,
        order_id=order_id,
        missing_items=missing,
        message="All medications available" if is_valid else f"{len(missing)} medication(s) unavailable",
    )


# ══════════════════════════════════════════════
#  3. PRESCRIPTION VERIFICATION
# ══════════════════════════════════════════════

@router.post(
    "/prescriptions/sign",
    response_model=PrescriptionSignResponse,
    summary="Generate Prescription Hash",
)
async def sign_prescription(body: PrescriptionSignRequest):
    """
    Generate a SHA-256 HMAC hash for a prescription payload.
    Store this hash alongside the order to enable later verification.
    """
    rx_hash = generate_prescription_hash(
        doctor_id=body.doctor_id,
        medications=body.medications,
        created_at=body.created_at,
    )
    return PrescriptionSignResponse(
        prescription_hash=rx_hash,
        doctor_id=body.doctor_id,
        medication_count=len(body.medications),
        signed_at=datetime.utcnow().isoformat() + "Z",
    )


@router.post(
    "/prescriptions/verify",
    response_model=PrescriptionVerifyResponse,
    summary="Verify Prescription Integrity",
)
async def verify_prescription_endpoint(body: PrescriptionVerifyRequest):
    """
    Verify that a prescription has not been tampered with since creation.
    Compares the stored hash against a freshly computed one.
    """
    is_valid, details = verify_prescription(
        doctor_id=body.doctor_id,
        medications=body.medications,
        created_at=body.created_at,
        expected_hash=body.expected_hash,
    )

    # Log verification in order timeline
    await log_prescription_verification(body.order_id, is_valid, body.doctor_id)

    return PrescriptionVerifyResponse(**details)


# ══════════════════════════════════════════════
#  4. ORDER TIMELINE
# ══════════════════════════════════════════════

@router.get(
    "/orders/{order_id}/timeline",
    response_model=List[TimelineEventResponse],
    summary="Get Order Timeline",
)
async def get_timeline(order_id: str):
    """
    Retrieve the full audit timeline for an order.
    Powers the "Tracking Timeline" view in Patient and Pharmacy frontends.
    """
    events = await get_order_timeline(order_id)
    return events


# ══════════════════════════════════════════════
#  5. EXPIRY CLEANUP AGENT
# ══════════════════════════════════════════════

@router.post(
    "/inventory/cleanup",
    response_model=ExpiryCleanupResponse,
    summary="Run Expiry Cleanup Agent",
)
async def run_expiry_cleanup(background_tasks: BackgroundTasks):
    """
    Scan inventory for items expiring within 30 days.
    Moves them to 'RESTRICTED' status so they cannot be added to new orders.

    This is the **Batch Processing & Expiry Agent** endpoint.
    """
    result = await cleanup_expiring_inventory()
    return result


# ══════════════════════════════════════════════
#  6. INVENTORY HEALTH
# ══════════════════════════════════════════════

@router.get(
    "/inventory/health",
    response_model=InventoryHealthResponse,
    summary="Inventory Health Report",
)
async def inventory_health():
    """
    Comprehensive inventory health summary including stock levels,
    expiry warnings, and an overall health score (0-100).
    """
    return await get_inventory_health()


# ══════════════════════════════════════════════
#  7. DELIVERY ROUTES (Leaflet Integration)
# ══════════════════════════════════════════════

@router.post(
    "/delivery/route",
    response_model=DeliveryRouteResponse,
    summary="Get Optimized Delivery Route",
)
async def get_delivery_route_endpoint(body: DeliveryRouteRequest):
    """
    Returns an optimized delivery path (array of waypoints) for a
    HOME_DELIVERY order. Designed for rendering on a Leaflet map.

    Waypoints include lat/lng coordinates, labels, and a suggested
    polyline color.
    """
    route = get_delivery_route(
        order_id=body.order_id,
        delivery_address=body.delivery_address,
    )
    return route


@router.post(
    "/delivery/batch-routes",
    summary="Get Batch Delivery Routes",
)
async def get_batch_routes(body: BatchRouteRequest):
    """
    Generate optimized routes for multiple orders at once.
    In production, applies TSP-like optimization across all destinations.
    """
    return get_batch_delivery_routes(body.order_ids)
