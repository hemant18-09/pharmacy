
import sys
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock firebase_admin modules BEFORE importing app components that use them
sys.modules["firebase_admin"] = MagicMock()
sys.modules["firebase_admin.auth"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()

# Import the router and necessary models
from app.routers import pharmacy_v2
from app.pharmacy.models import PrescriptionStatus

class TestPharmacyV2Endpoint(unittest.TestCase):
    def setUp(self):
        # Create a clean FastAPI app for testing just this router
        self.app = FastAPI()
        self.app.include_router(pharmacy_v2.router)
        self.client = TestClient(self.app)

    @patch("app.routers.pharmacy_v2.validate_stock_for_order", new_callable=AsyncMock)
    def test_validate_stock_success(self, mock_validate):
        # Setup mock
        mock_validate.return_value = (True, [])

        response = self.client.get("/pharmacy/v2/orders/ord-123/validate-stock")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_valid"])
        self.assertEqual(data["order_id"], "ord-123")
        self.assertEqual(data["missing_items"], [])

    @patch("app.routers.pharmacy_v2.validate_stock_for_order", new_callable=AsyncMock)
    def test_validate_stock_failure(self, mock_validate):
        # Setup mock for failure
        mock_validate.return_value = (False, [{"name": "Aspirin", "needed": 10, "available": 5}])

        response = self.client.get("/pharmacy/v2/orders/ord-123/validate-stock")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_valid"])
        self.assertEqual(len(data["missing_items"]), 1)
        self.assertEqual(data["missing_items"][0]["name"], "Aspirin")

    @patch("app.routers.pharmacy_v2.generate_prescription_hash")
    def test_sign_prescription(self, mock_hash):
        mock_hash.return_value = "hashed_value_123"
        
        payload = {
            "doctor_id": "doc-001",
            "medications": [{"name": "Meds", "qty": 1}],
            "created_at": "2023-01-01T12:00:00Z"
        }
        
        response = self.client.post("/pharmacy/v2/prescriptions/sign", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["prescription_hash"], "hashed_value_123")
        self.assertEqual(data["doctor_id"], "doc-001")

    @patch("app.routers.pharmacy_v2.order_service.get_order_detail", new_callable=AsyncMock)
    @patch("app.routers.pharmacy_v2.order_service.update_order_status", new_callable=AsyncMock)
    @patch("app.routers.pharmacy_v2.log_status_change", new_callable=AsyncMock)

    def test_agentic_status_update_basic(self, mock_log, mock_update, mock_get):
        # Test simple transition (e.g. PREPARING -> READY) which doesn't check stock
        mock_get.return_value = {"order_id": "ord-123", "status": PrescriptionStatus.PREPARING}
        mock_update.return_value = {
            "id": "ord-123", 
            "status": PrescriptionStatus.READY,
            "color_code": "green"
        }

        payload = {
            "status": PrescriptionStatus.READY,
            "actor_id": "pharmacist-1"
        }
        
        response = self.client.patch("/pharmacy/v2/orders/ord-123/status", json=payload)
        
        self.assertEqual(response.status_code, 200)
        mock_update.assert_called_with("ord-123", PrescriptionStatus.READY)
        # Background tasks might not execute immediately in TestClient unless using BackgroundTasks logic, 
        # but in Starlette TestClient, they are usually collected.
        # We verify that update was called.

    @patch("app.routers.pharmacy_v2.order_service.get_order_detail", new_callable=AsyncMock)
    @patch("app.routers.pharmacy_v2.validate_stock_for_order", new_callable=AsyncMock)
    def test_agentic_status_update_insufficient_stock(self, mock_validate, mock_get):
        # Test NEW -> ACCEPTED where stock is missing
        mock_get.return_value = {"order_id": "ord-123", "status": PrescriptionStatus.NEW}
        mock_validate.return_value = (False, [{"name": "Meds", "error": "None"}])

        payload = {
            "status": PrescriptionStatus.ACCEPTED,
            "actor_id": "pharmacist-1"
        }
        
        response = self.client.patch("/pharmacy/v2/orders/ord-123/status", json=payload)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["error"], "INSUFFICIENT_STOCK")



if __name__ == "__main__":
    import io
    runner = unittest.TextTestRunner(stream=open("test_run_utf8.log", "w", encoding="utf-8"), verbosity=2)
    unittest.main(testRunner=runner, exit=False)
