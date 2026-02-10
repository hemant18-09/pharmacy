"""
Pydantic Models & Firestore Schema for the DOC AI Pharmacy Portal.

Collections:
  - pharmacy_orders/{order_id}   → PharmacyOrder document
  - pharmacists/{pharmacist_id}  → PharmacistProfile document
"""

from __future__ import annotations

from enum import Enum
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ──────────────────────────────────────────────
# 1. Enums & Constants
# ──────────────────────────────────────────────

class PrescriptionStatus(str, Enum):
    """Maps 1-to-1 with UI status chips."""
    NEW = "NEW"                # Default – just arrived
    ACCEPTED = "ACCEPTED"      # Pharmacist acknowledged
    PREPARING = "PREPARING"    # Amber chip – being prepared
    READY = "READY"            # Green chip – ready for handoff
    DELIVERED = "DELIVERED"    # Green chip – home-delivery complete
    PICKED_UP = "PICKED_UP"   # Patient collected from store
    REJECTED = "REJECTED"      # Order cancelled by pharmacy


class DeliveryMode(str, Enum):
    HOME_DELIVERY = "HOME_DELIVERY"
    STORE_PICKUP = "STORE_PICKUP"


# ──────────────────────────────────────────────
# 2. Embedded / Nested Models
# ──────────────────────────────────────────────

class PatientInfo(BaseModel):
    """Lightweight patient snapshot stored on every order."""
    name: str
    age: int
    gender: str
    contact_id: str = Field(
        ..., description="Reference to the patient's contact record (phone / email)"
    )


class DoctorInfo(BaseModel):
    """Prescribing doctor snapshot."""
    name: str
    registration_id: str = Field(
        ..., description="Doctor medical-council registration number"
    )


class MedicationItem(BaseModel):
    """
    Single line-item in a prescription.
    Column mapping mirrors the frontend table exactly.
    """
    drug_name: str = Field(..., description="Brand / generic drug name")
    strength: str = Field(..., description="e.g. '500mg', '10mg/5ml'")
    frequency: str = Field(..., description="e.g. '1-0-1' (morning-afternoon-night)")
    duration: str = Field(..., description="e.g. '5 Days', '2 Weeks'")
    instructions: str = Field(
        default="", description="e.g. 'After food', 'Before bed'"
    )


class OrderTimestamps(BaseModel):
    """Lifecycle timestamps – populated as the order progresses."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: Optional[datetime] = None
    ready_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ──────────────────────────────────────────────
# 3. PharmacyOrder  (Firestore: pharmacy_orders/{id})
# ──────────────────────────────────────────────

class PharmacyOrder(BaseModel):
    """
    Root document stored in Firestore under `pharmacy_orders/{id}`.
    Represents a single prescription sent to the pharmacy.
    """
    id: str = Field(..., description="Firestore document ID")
    patient_info: PatientInfo
    doctor_info: DoctorInfo
    medications: List[MedicationItem]
    status: PrescriptionStatus = PrescriptionStatus.NEW
    delivery_mode: DeliveryMode = DeliveryMode.STORE_PICKUP
    timestamps: OrderTimestamps = Field(default_factory=OrderTimestamps)

    model_config = ConfigDict(use_enum_values=True)


# ──────────────────────────────────────────────
# 4. PharmacistProfile  (Firestore: pharmacists/{id})
# ──────────────────────────────────────────────

class NotificationPreferences(BaseModel):
    """Channels the pharmacist wants alerts on."""
    email: bool = True
    sms: bool = False
    push: bool = True


class PharmacistProfile(BaseModel):
    """
    Profile document for a registered pharmacist.
    Stored in Firestore under `pharmacists/{pharmacist_id}`.
    """
    id: str = Field(..., description="Firestore document ID / UID")
    pharmacy_name: str
    license_no: str = Field(..., description="Pharmacy license number")
    operating_hours: str = Field(
        ..., description="e.g. '09:00 – 21:00' or 'Mon-Sat 9AM-9PM'"
    )
    notification_preferences: NotificationPreferences = Field(
        default_factory=NotificationPreferences
    )

    model_config = ConfigDict(use_enum_values=True)


# ──────────────────────────────────────────────
# 5. InventoryItem  (Firestore: pharmacy_inventory/{id})
# ──────────────────────────────────────────────

class InventoryItem(BaseModel):
    """
    A single stock-keeping row in the pharmacy inventory.
    Stored in Firestore under `pharmacy_inventory/{id}`.
    """
    id: str = Field(..., description="Firestore document ID")
    drug_name: str
    strength: str = Field(..., description="e.g. '500mg'")
    quantity: int = Field(..., ge=0, description="Current stock count")
    expiry_date: datetime = Field(..., description="Batch expiry date")
    batch_number: str = Field(..., description="Manufacturer batch ID")
    threshold: int = Field(default=10, description="Low-stock warning threshold")

    model_config = ConfigDict(use_enum_values=True)


# ──────────────────────────────────────────────
# 6. Chat / Messaging  (Firestore: pharmacy_chats/{order_id}/messages/{msg_id})
# ──────────────────────────────────────────────

class ChatMessageSender(str, Enum):
    PHARMACIST = "PHARMACIST"
    PATIENT = "PATIENT"


class ChatMessage(BaseModel):
    """
    A single message in a pharmacy ↔ patient conversation.
    Subcollection: pharmacy_chats/{order_id}/messages/{id}
    """
    id: str = Field(..., description="Message document ID")
    order_id: str = Field(..., description="Parent order this chat belongs to")
    sender: ChatMessageSender
    message: str
    category: str = Field(
        default="general",
        description="Message topic: 'delivery' | 'availability' | 'general'",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(use_enum_values=True)
