"""
Request / Response schemas for Pharmacy Portal API endpoints.
Thin wrappers around the core models to separate API concerns.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from .models import (
    DeliveryMode,
    MedicationItem,
    PrescriptionStatus,
)


# ── Requests ──────────────────────────────────

class CreateOrderRequest(BaseModel):
    """Body sent when a new prescription arrives at the pharmacy."""
    patient_name: str
    patient_age: int
    patient_gender: str
    patient_contact_id: str
    doctor_name: str
    doctor_registration_id: str
    medications: List[MedicationItem]
    delivery_mode: DeliveryMode = DeliveryMode.STORE_PICKUP


class CreateOrderBridgeRequest(BaseModel):
    """
    Request payload for creating an order from a prescription (Bridge).
    """
    case_id: str
    profile_id: str
    pharmacy_id: str
    items: List[dict]  # Simplified for flexibility, or use specialized MedicationItem if strict
    location: str


class PharmacyListItem(BaseModel):
    """
    Used by Patient Portal to select a pharmacy.
    """
    id: str
    name: str
    location: dict  # {lat, lng, address}
    is_verified: bool
    rating: float



class UpdateOrderStatusRequest(BaseModel):
    """PATCH body to advance an order through its lifecycle."""
    status: PrescriptionStatus


# ── Responses ─────────────────────────────────

# Dashboard cards -------------------------------------------------

class DashboardStatsResponse(BaseModel):
    """The 4 metric cards rendered at the top of the pharmacy dashboard."""
    new_prescriptions_today: int = Field(..., description="NEW orders created in last 24 h")
    orders_in_progress: int = Field(..., description="ACCEPTED + PREPARING count")
    orders_delivered_today: int = Field(..., description="DELIVERED + PICKED_UP in last 24 h")
    low_stock_alerts: int = Field(..., description="Inventory items below threshold")


# Order list (sidebar / table) ------------------------------------

class OrderListItem(BaseModel):
    """
    Lightweight order row used in the sidebar list / table.
    Includes a ``color_code`` hint so the frontend can render the
    correct chip colour without a second mapping.
    """
    id: str
    patient_name: str
    status: PrescriptionStatus
    color_code: str = Field(
        ..., description="UI chip colour: teal | blue | amber | green | gray"
    )
    medication_count: int
    created_at: Optional[str] = None  # ISO-8601
    accepted_at: Optional[str] = None
    ready_at: Optional[str] = None
    completed_at: Optional[str] = None


class OrderSummary(BaseModel):
    """Kept for backward-compat – identical to OrderListItem minus color_code."""
    id: str
    patient_name: str
    status: PrescriptionStatus
    medication_count: int
    created_at: str


# Order detail ----------------------------------------------------

class OrderDetailResponse(BaseModel):
    """Full order detail returned on click / GET by ID."""
    id: str
    patient_name: str
    patient_age: int
    patient_gender: str
    patient_contact_id: str
    doctor_name: str
    doctor_registration_id: str
    medications: List[MedicationItem]
    status: PrescriptionStatus
    color_code: Optional[str] = None
    delivery_mode: DeliveryMode
    created_at: Optional[str] = None
    accepted_at: Optional[str] = None
    ready_at: Optional[str] = None
    completed_at: Optional[str] = None


# Status update confirmation --------------------------------------

class StatusUpdateResponse(BaseModel):
    """Returned after a successful PATCH on order status."""
    id: str
    status: PrescriptionStatus
    color_code: str
    updated_at: Optional[str] = None


# ══════════════════════════════════════════════
#  INVENTORY Schemas
# ══════════════════════════════════════════════

class InventoryItemResponse(BaseModel):
    """A single inventory row with computed warning flags."""
    id: str
    drug_name: str
    strength: str
    quantity: int
    expiry_date: Optional[str] = None  # ISO-8601
    batch_number: str
    threshold: int = 10
    is_low_stock: bool = Field(
        False, description="True when quantity < threshold → Red warning"
    )
    is_expiring_soon: bool = Field(
        False, description="True when expiry < 30 days → Yellow warning"
    )


class UpdateStockRequest(BaseModel):
    """POST body for /pharmacy/inventory/update."""
    item_id: str
    quantity: int = Field(..., ge=0, description="New stock count")


class AddInventoryRequest(BaseModel):
    """POST body for /pharmacy/inventory/add."""
    drug_name: str
    batch_number: str
    expiry_date: str
    quantity: int
    strength: str = ""
    threshold: int = 10


# ══════════════════════════════════════════════
#  REPORTS Schemas
# ══════════════════════════════════════════════

class DailySummaryItem(BaseModel):
    """One data point on the 'Orders per day' chart."""
    date: str = Field(..., description="YYYY-MM-DD")
    label: str = Field(..., description="Human-readable label, e.g. 'Feb 08'")
    total_orders: int
    delivered: int
    new: int


class TopMedicineItem(BaseModel):
    """One bar on the 'Most Dispensed' horizontal chart."""
    drug_name: str
    count: int
    rank: int


# ══════════════════════════════════════════════
#  CHAT / MESSAGING Schemas
# ══════════════════════════════════════════════

class SendMessageRequest(BaseModel):
    """POST body for /pharmacy/chat/send."""
    order_id: str
    sender: str = Field(
        ..., description="'PHARMACIST' or 'PATIENT'"
    )
    message: str = Field(..., min_length=1, max_length=2000)
    category: str = Field(
        default="general",
        description="Message topic: 'delivery' | 'availability' | 'general'",
    )


class ChatMessageResponse(BaseModel):
    """A single chat message."""
    id: str
    order_id: str
    sender: str
    message: str
    category: str = "general"
    created_at: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """Full chat thread for an order."""
    order_id: str
    is_locked: bool = Field(
        False,
        description="True when order is DELIVERED / PICKED_UP → chat is read-only",
    )
    messages: List[ChatMessageResponse] = []
