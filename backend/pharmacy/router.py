"""
FastAPI Router – Pharmacy Portal
Prefix: /pharmacy

Endpoints:
  GET  /pharmacy/stats                    → Dashboard metric cards
  GET  /pharmacy/orders                   → Filtered order list (sidebar)
  GET  /pharmacy/orders/{order_id}        → Full order detail
  PATCH /pharmacy/orders/{order_id}/status → Advance order status
  POST /pharmacy/orders                   → Create a new order
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from pharmacy.models import PrescriptionStatus
from pharmacy.schemas import (
    CreateOrderRequest,
    CreateOrderBridgeRequest,
    DashboardStatsResponse,
    OrderDetailResponse,
    OrderListItem,
    StatusUpdateResponse,
    UpdateOrderStatusRequest,
)

from pharmacy.schemas_signup import PharmacySignupRequest

from pharmacy import service
from app.core.firebase import firebase_service
import uuid
from firebase_admin import auth, firestore
import firebase_admin


router = APIRouter(prefix="/pharmacy", tags=["Pharmacy Portal"])

@router.get("/")
async def pharmacy_root():
    return {"message": "Pharmacy API is online", "endpoints": ["/stats", "/orders", "/inventory"]}

# ──────────────────────────────────────────────
# 0.  Pharmacy Signup
# ──────────────────────────────────────────────

@router.post("/signup", status_code=201)
async def pharmacy_signup(req: PharmacySignupRequest):
    """
    Registers a new LINKED pharmacist and pharmacy.
    1. Creates User in Firebase Auth
    2. Creates 'pharmacies' doc
    3. Creates 'users' doc with role='pharmacist' & pharmacy_id linked
    """
    
    email = req.email
    password = req.password
    
    # 1. Access DB
    db = firebase_service.db
    if not db and not firebase_service.mock_mode:
         raise HTTPException(status_code=500, detail="Database connection not available")
         
    if firebase_service.mock_mode:
         return {"status": "success", "pharmacy_id": "MOCK-PHARMACY-ID", "uid": "MOCK-UID"}

    # 2. Firebase Auth - Create User
    try:
        app_instance = firebase_service.app or firebase_admin.get_app()
        user = auth.create_user(
            email=email, 
            password=password, 
            app=app_instance
        )
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth Error: {str(e)}")

    uid = user.uid

    # 3. Create Pharmacy Document
    pharmacy_id = str(uuid.uuid4())
    pharmacy_data = {
        "name": req.pharmacy_name,
        "license_number": req.license_no,
        "location": req.location,
        "created_at": firestore.SERVER_TIMESTAMP,
        "owner_uid": uid
    }
    
    try:
        db.collection("pharmacies").document(pharmacy_id).set(pharmacy_data)

        # 4. Create User Document with Link
        user_data = {
            "uid": uid,
            "email": email,
            "role": "pharmacist",
            "pharmacy_id": pharmacy_id,
            "is_verified": False,  # Block access until admin check
            "created_at": firestore.SERVER_TIMESTAMP
        }
        db.collection("users").document(uid).set(user_data)
        
        return {"status": "success", "pharmacy_id": pharmacy_id, "uid": uid}

    except Exception as e:
        # In a real app, we might want to rollback the Auth user creation here
        raise HTTPException(status_code=500, detail=f"Firestore Error: {str(e)}")


# ──────────────────────────────────────────────
# 0.b  Pharmacy List (for Patient Portal to Select)
# ──────────────────────────────────────────────

from pharmacy.schemas import PharmacyListItem

@router.get("/list", response_model=List[PharmacyListItem])
async def list_verified_pharmacies(
    lat: Optional[float] = Query(None, description="Patient latitude for sorting"),
    lng: Optional[float] = Query(None, description="Patient longitude for sorting")
):
    """
    Returns a list of verified pharmacies.
    Used by the Patient Portal when the user clicks 'Order Now'.
    """
    pharmacies = await service.list_pharmacies(lat, lng)
    return pharmacies


@router.get("/stats", response_model=DashboardStatsResponse)
async def pharmacy_dashboard_stats():
    """Return the 4 metric cards for the pharmacy dashboard."""
    data = await service.get_dashboard_stats()
    return data


# ──────────────────────────────────────────────
# 2.  Order List  (sidebar / table)
# ──────────────────────────────────────────────

@router.get("/orders", response_model=List[OrderListItem])
async def list_pharmacy_orders(
    status: Optional[PrescriptionStatus] = Query(
        None, description="Filter by prescription status (NEW, ACCEPTED, PREPARING …)"
    ),
    date_from: Optional[datetime] = Query(
        None, description="Start of date range (ISO-8601)"
    ),
    date_to: Optional[datetime] = Query(
        None, description="End of date range (ISO-8601)"
    ),
):
    """
    Paginated / filtered order list.
    Each item carries a **color_code** hint for the UI chip.
    """
    orders = await service.list_orders(
        status=status.value if status else None,
        date_from=date_from,
        date_to=date_to,
    )
    return orders


# ──────────────────────────────────────────────
# 3.  Order Detail
# ──────────────────────────────────────────────

@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
async def get_pharmacy_order(order_id: str):
    """Full order detail including Patient card, Doctor card, and medication table."""
    detail = await service.get_order_detail(order_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return detail


# ──────────────────────────────────────────────
# 4.  Status Transition
# ──────────────────────────────────────────────

@router.patch("/orders/{order_id}/status", response_model=StatusUpdateResponse)
async def update_pharmacy_order_status(
    order_id: str,
    body: UpdateOrderStatusRequest,
):
    """
    Advance an order through its lifecycle.
    Side-effects:
      * READY     → push notification sent to patient
      * DELIVERED  → `completed_at` timestamp recorded
      * PICKED_UP  → `completed_at` timestamp recorded
    """
    result = await service.update_order_status(order_id, body.status)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return result


# ──────────────────────────────────────────────
# 5.  Create Order  (prescription → pharmacy)
# ──────────────────────────────────────────────

@router.post("/orders", response_model=dict, status_code=201)
async def create_pharmacy_order(body: CreateOrderRequest):
    """Accept a new prescription from the doctor / agent flow."""
    meds = [m.dict() for m in body.medications]
    result = await service.create_order(
        patient_name=body.patient_name,
        patient_age=body.patient_age,
        patient_gender=body.patient_gender,
        patient_contact_id=body.patient_contact_id,
        doctor_name=body.doctor_name,
        doctor_registration_id=body.doctor_registration_id,
        medications=meds,
        delivery_mode=body.delivery_mode,
    )
    return result


# ──────────────────────────────────────────────
# 6.  Prescription Bridge
# ──────────────────────────────────────────────

@router.post("/create_order")
async def create_order_from_prescription(order_req: CreateOrderBridgeRequest):
    """
    Final bridge: Patient selects a pharmacy and clicks 'Order'.
    Adapts the request to the Pharmacy Portal schema (v2) while keeping v1 IDs.
    """
    try:
        # 1. Fetch Profile Data (for Name/Age)
        patient_name = "Unknown Patient"
        patient_age = 0
        patient_gender = "Unknown"
        
        if not firebase_service.mock_mode:
            try:
                doc = firebase_service.db.collection("profiles").document(order_req.profile_id).get()
                if doc.exists:
                    p_data = doc.to_dict()
                    patient_name = p_data.get("full_name", patient_name)
                    patient_gender = p_data.get("gender", patient_gender)
                    # Calculate age from DOB if available
                    dob_str = p_data.get("dob")
                    if dob_str:
                        # Simple year diff
                        dob_year = int(dob_str[:4])
                        patient_age = datetime.utcnow().year - dob_year
            except Exception as e:
                print(f"Profile Fetch Warning: {e}")

        # 2. Structure for Pharmacy Portal (matches service.py schema)
        now = datetime.utcnow()
        order_id = f"RX-{uuid.uuid4().hex[:8].upper()}"
        
        # Simplified medication mapping
        meds = []
        for item in order_req.items:
            meds.append({
                "drug_name": item.get("drug_name", "Unknown Drug"),
                "strength": item.get("strength", "N/A"),
                "frequency": item.get("frequency", "N/A"),
                "duration": item.get("duration", "N/A"),
                "instructions": item.get("instructions", "N/A"),
                "quantity": item.get("quantity", 1)
            })

        new_order = {
            "order_id": order_id,
            "patient_info": {
                "name": patient_name,
                "age": patient_age,
                "gender": patient_gender,
                "contact_id": order_req.profile_id
            },
            "doctor_info": {
                "name": "Dr. Assigned",
                "registration_id": "REG-000"
            },
            "medications": meds,
            "status": "NEW",
            "delivery_mode": "STORE_PICKUP",
            "timestamps": {
                "created_at": now,
                "accepted_at": None,
                "ready_at": None,
                "completed_at": None
            },
            # Bridge specific fields
            "case_id": order_req.case_id,
            "profile_id": order_req.profile_id,
            "pharmacy_id": order_req.pharmacy_id,
            "delivery_location": order_req.location
        }
        
        # Save directly to 'pharmacy_orders'
        if not firebase_service.mock_mode:
            firebase_service.db.collection("pharmacy_orders").document(order_id).set(new_order)
        else:
            print(f"[MOCK] Bridge Created Order: {new_order}")

        return {"status": "success", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

