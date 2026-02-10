from typing import List, Tuple
from datetime import datetime

def generate_prescription_hash(doctor_id: str, medications: List[dict], created_at: str) -> str:
    # Mock implementation
    return "mock_hash_1234567890abcdef"

def verify_prescription(doctor_id: str, medications: List[dict], created_at: str, expected_hash: str) -> Tuple[bool, dict]:
    # Mock implementation
    return True, {
        "is_valid": True,
        "doctor_id": doctor_id,
        "medication_count": len(medications),
        "computed_hash_prefix": "mock_hash...",
        "expected_hash_prefix": "mock_hash...",
        "verified_at": datetime.utcnow().isoformat() + "Z",
        "verdict": "INTEGRITY_VERIFIED"
    }

def sign_order_payload(order_payload: dict) -> str:
    # Mock implementation
    return "signed_payload_mock"
