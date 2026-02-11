from datetime import datetime, timedelta
from pharmacy.models import PrescriptionStatus, DeliveryMode

def _now():
    return datetime.utcnow()

def _ts_to_iso(dt):
    if not dt:
        return None
    return dt.isoformat() + "Z"

def get_initial_mock_orders():
    now = _now()
    return [
        # --- NEW ORDERS (8 total for a busy queue) ---
        {
            "id": "RX-1001",
            "patient_info": {"name": "Aarav Sharma", "age": 34, "gender": "Male", "contact_id": "PAT-9001"},
            "doctor_info": {"name": "Dr. Meena Iyer", "registration_id": "MCI-78432"},
            "medications": [
                {"drug_name": "Amoxicillin", "strength": "500mg", "frequency": "1-0-1", "duration": "5 Days", "instructions": "After food"},
                {"drug_name": "Paracetamol", "strength": "650mg", "frequency": "1-1-1", "duration": "3 Days", "instructions": "As needed"}
            ],
            "status": PrescriptionStatus.NEW,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 245.00,
            "timestamps": {"created_at": _ts_to_iso(now - timedelta(minutes=10)), "accepted_at": None, "ready_at": None, "completed_at": None}
        },
        {
            "id": "RX-1006",
            "patient_info": {"name": "Anita Desai", "age": 28, "gender": "Female", "contact_id": "PAT-9006"},
            "doctor_info": {"name": "Dr. Ravi Kumar", "registration_id": "MCI-88123"},
            "medications": [
                {"drug_name": "Cetirizine", "strength": "10mg", "frequency": "0-0-1", "duration": "5 Days", "instructions": "At night"},
                {"drug_name": "Vitamin C", "strength": "500mg", "frequency": "1-0-0", "duration": "10 Days", "instructions": "With water"}
            ],
            "status": PrescriptionStatus.NEW,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 180.00,
            "timestamps": {"created_at": _ts_to_iso(now - timedelta(minutes=25)), "accepted_at": None, "ready_at": None, "completed_at": None}
        },
        {
            "id": "RX-1011",
            "patient_info": {"name": "Karan Mehta", "age": 45, "gender": "Male", "contact_id": "PAT-9011"},
            "doctor_info": {"name": "Dr. S. Gupta", "registration_id": "MCI-55678"},
            "medications": [{"drug_name": "Metformin", "strength": "500mg", "frequency": "1-0-1", "duration": "30 Days", "instructions": "With meals"}],
            "status": PrescriptionStatus.NEW,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 320.00,
            "timestamps": {"created_at": _ts_to_iso(now - timedelta(minutes=45)), "accepted_at": None, "ready_at": None, "completed_at": None}
        },
        {
            "id": "RX-1012",
            "patient_info": {"name": "Deepika Rao", "age": 31, "gender": "Female", "contact_id": "PAT-9012"},
            "doctor_info": {"name": "Dr. Meena Iyer", "registration_id": "MCI-78432"},
            "medications": [
                {"drug_name": "Pantoprazole", "strength": "40mg", "frequency": "1-0-0", "duration": "14 Days", "instructions": "Before breakfast"},
                {"drug_name": "Domperidone", "strength": "10mg", "frequency": "1-1-1", "duration": "7 Days", "instructions": "Before food"}
            ],
            "status": PrescriptionStatus.NEW,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 290.00,
            "timestamps": {"created_at": _ts_to_iso(now - timedelta(minutes=5)), "accepted_at": None, "ready_at": None, "completed_at": None}
        },
        {
            "id": "RX-1013",
            "patient_info": {"name": "Suresh Nair", "age": 55, "gender": "Male", "contact_id": "PAT-9013"},
            "doctor_info": {"name": "Dr. V. Rao", "registration_id": "MCI-44556"},
            "medications": [
                {"drug_name": "Losartan", "strength": "50mg", "frequency": "1-0-0", "duration": "30 Days", "instructions": "Morning"},
                {"drug_name": "Aspirin", "strength": "75mg", "frequency": "0-1-0", "duration": "30 Days", "instructions": "After lunch"},
                {"drug_name": "Atorvastatin", "strength": "10mg", "frequency": "0-0-1", "duration": "30 Days", "instructions": "At bedtime"}
            ],
            "status": PrescriptionStatus.NEW,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 685.00,
            "timestamps": {"created_at": _ts_to_iso(now - timedelta(minutes=18)), "accepted_at": None, "ready_at": None, "completed_at": None}
        },
        {
            "id": "RX-1014",
            "patient_info": {"name": "Meera Krishnan", "age": 38, "gender": "Female", "contact_id": "PAT-9014"},
            "doctor_info": {"name": "Dr. K. Nair", "registration_id": "MCI-99887"},
            "medications": [
                {"drug_name": "Escitalopram", "strength": "10mg", "frequency": "0-0-1", "duration": "30 Days", "instructions": "At night"}
            ],
            "status": PrescriptionStatus.NEW,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 350.00,
            "timestamps": {"created_at": _ts_to_iso(now - timedelta(minutes=32)), "accepted_at": None, "ready_at": None, "completed_at": None}
        },
        {
            "id": "RX-1015",
            "patient_info": {"name": "Rajan Pillai", "age": 62, "gender": "Male", "contact_id": "PAT-9015"},
            "doctor_info": {"name": "Dr. Arjun Singh", "registration_id": "MCI-12903"},
            "medications": [
                {"drug_name": "Telmisartan", "strength": "40mg", "frequency": "1-0-0", "duration": "30 Days", "instructions": "Morning"},
                {"drug_name": "Amlodipine", "strength": "5mg", "frequency": "1-0-0", "duration": "30 Days", "instructions": "Morning"}
            ],
            "status": PrescriptionStatus.NEW,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 520.00,
            "timestamps": {"created_at": _ts_to_iso(now - timedelta(minutes=55)), "accepted_at": None, "ready_at": None, "completed_at": None}
        },
        {
            "id": "RX-1016",
            "patient_info": {"name": "Fatima Begum", "age": 42, "gender": "Female", "contact_id": "PAT-9016"},
            "doctor_info": {"name": "Dr. Ravi Kumar", "registration_id": "MCI-88123"},
            "medications": [
                {"drug_name": "Montelukast", "strength": "10mg", "frequency": "0-0-1", "duration": "14 Days", "instructions": "At night"},
                {"drug_name": "Albuterol Inhaler", "strength": "90mcg", "frequency": "SOS", "duration": "30 Days", "instructions": "As needed"}
            ],
            "status": PrescriptionStatus.NEW,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 475.00,
            "timestamps": {"created_at": _ts_to_iso(now - timedelta(minutes=12)), "accepted_at": None, "ready_at": None, "completed_at": None}
        },

        # --- ACCEPTED ORDERS ---
        {
            "id": "RX-1002",
            "patient_info": {"name": "Priya Patel", "age": 29, "gender": "Female", "contact_id": "PAT-9002"},
            "doctor_info": {"name": "Dr. Arjun Singh", "registration_id": "MCI-12903"},
            "medications": [
                {"drug_name": "Ibuprofen", "strength": "400mg", "frequency": "1-0-1", "duration": "3 Days", "instructions": "After food"}
            ],
            "status": PrescriptionStatus.ACCEPTED,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 120.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(hours=2)),
                "accepted_at": _ts_to_iso(now - timedelta(hours=1, minutes=30)),
                "ready_at": None,
                "completed_at": None
            }
        },
        {
            "id": "RX-1009",
            "patient_info": {"name": "Amit Shah", "age": 52, "gender": "Male", "contact_id": "PAT-9009"},
            "doctor_info": {"name": "Dr. V. Rao", "registration_id": "MCI-44556"},
            "medications": [
                {"drug_name": "Atorvastatin", "strength": "10mg", "frequency": "0-0-1", "duration": "30 Days", "instructions": "At bedtime"},
                {"drug_name": "Aspirin", "strength": "75mg", "frequency": "0-1-0", "duration": "30 Days", "instructions": "After lunch"}
            ],
            "status": PrescriptionStatus.ACCEPTED,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 410.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(hours=3)),
                "accepted_at": _ts_to_iso(now - timedelta(hours=2, minutes=15)),
                "ready_at": None,
                "completed_at": None
            }
        },

        # --- PREPARING ORDERS ---
        {
            "id": "RX-1003",
            "patient_info": {"name": "Rohan Gupta", "age": 41, "gender": "Male", "contact_id": "PAT-9003"},
            "doctor_info": {"name": "Dr. Meena Iyer", "registration_id": "MCI-78432"},
            "medications": [
                {"drug_name": "Augmentin", "strength": "625mg", "frequency": "1-0-1", "duration": "5 Days", "instructions": "Complete course"},
                {"drug_name": "B-Complex", "strength": "1 tab", "frequency": "1-0-0", "duration": "10 Days", "instructions": "Once daily"}
            ],
            "status": PrescriptionStatus.PREPARING,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 380.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(hours=4)),
                "accepted_at": _ts_to_iso(now - timedelta(hours=3, minutes=30)),
                "ready_at": None,
                "completed_at": None
            }
        },
        {
            "id": "RX-1010",
            "patient_info": {"name": "Neha Joshi", "age": 33, "gender": "Female", "contact_id": "PAT-9010"},
            "doctor_info": {"name": "Dr. K. Nair", "registration_id": "MCI-99887"},
            "medications": [{"drug_name": "Thyroxine", "strength": "50mcg", "frequency": "1-0-0", "duration": "60 Days", "instructions": "Empty stomach"}],
            "status": PrescriptionStatus.PREPARING,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 195.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(hours=5)),
                "accepted_at": _ts_to_iso(now - timedelta(hours=4, minutes=15)),
                "ready_at": None,
                "completed_at": None
            }
        },

        # --- READY ORDERS ---
        {
            "id": "RX-1004",
            "patient_info": {"name": "Sneha Reddy", "age": 25, "gender": "Female", "contact_id": "PAT-9004"},
            "doctor_info": {"name": "Dr. Arjun Singh", "registration_id": "MCI-12903"},
            "medications": [{"drug_name": "Sumatriptan", "strength": "50mg", "frequency": "SOS", "duration": "5 Days", "instructions": "For migraine"}],
            "status": PrescriptionStatus.READY,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 210.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(hours=6)),
                "accepted_at": _ts_to_iso(now - timedelta(hours=5, minutes=30)),
                "ready_at": _ts_to_iso(now - timedelta(hours=4)),
                "completed_at": None
            }
        },

        # --- DELIVERED/PICKED UP ORDERS (multiple days for chart data) ---
        {
            "id": "RX-1005",
            "patient_info": {"name": "Vikram Singh", "age": 60, "gender": "Male", "contact_id": "PAT-9005"},
            "doctor_info": {"name": "Dr. V. Rao", "registration_id": "MCI-44556"},
            "medications": [
                {"drug_name": "Amlodipine", "strength": "5mg", "frequency": "1-0-0", "duration": "30 Days", "instructions": "Morning"},
                {"drug_name": "Telmisartan", "strength": "40mg", "frequency": "1-0-0", "duration": "30 Days", "instructions": "Morning"}
            ],
            "status": PrescriptionStatus.DELIVERED,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 560.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(hours=8)),
                "accepted_at": _ts_to_iso(now - timedelta(hours=7)),
                "ready_at": _ts_to_iso(now - timedelta(hours=6)),
                "completed_at": _ts_to_iso(now - timedelta(hours=5))
            }
        },
        {
            "id": "RX-1008",
            "patient_info": {"name": "Kavita Kapoor", "age": 45, "gender": "Female", "contact_id": "PAT-9008"},
            "doctor_info": {"name": "Dr. S. Gupta", "registration_id": "MCI-55678"},
            "medications": [{"drug_name": "Calcium D3", "strength": "500mg", "frequency": "0-1-0", "duration": "30 Days", "instructions": "After lunch"}],
            "status": PrescriptionStatus.PICKED_UP,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 180.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(hours=10)),
                "accepted_at": _ts_to_iso(now - timedelta(hours=9)),
                "ready_at": _ts_to_iso(now - timedelta(hours=8, minutes=30)),
                "completed_at": _ts_to_iso(now - timedelta(hours=7))
            }
        },
        # Additional historical orders for chart richness
        {
            "id": "RX-0990",
            "patient_info": {"name": "Ramesh Kumar", "age": 50, "gender": "Male", "contact_id": "PAT-8990"},
            "doctor_info": {"name": "Dr. Meena Iyer", "registration_id": "MCI-78432"},
            "medications": [
                {"drug_name": "Metformin", "strength": "500mg", "frequency": "1-0-1", "duration": "30 Days", "instructions": "With meals"},
                {"drug_name": "Glimepiride", "strength": "2mg", "frequency": "1-0-0", "duration": "30 Days", "instructions": "Before breakfast"}
            ],
            "status": PrescriptionStatus.DELIVERED,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 420.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(days=1, hours=6)),
                "accepted_at": _ts_to_iso(now - timedelta(days=1, hours=5)),
                "ready_at": _ts_to_iso(now - timedelta(days=1, hours=4)),
                "completed_at": _ts_to_iso(now - timedelta(days=1, hours=2))
            }
        },
        {
            "id": "RX-0991",
            "patient_info": {"name": "Lakshmi Devi", "age": 68, "gender": "Female", "contact_id": "PAT-8991"},
            "doctor_info": {"name": "Dr. Arjun Singh", "registration_id": "MCI-12903"},
            "medications": [
                {"drug_name": "Amlodipine", "strength": "5mg", "frequency": "1-0-0", "duration": "30 Days", "instructions": "Morning"},
            ],
            "status": PrescriptionStatus.DELIVERED,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 150.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(days=1, hours=4)),
                "accepted_at": _ts_to_iso(now - timedelta(days=1, hours=3)),
                "ready_at": _ts_to_iso(now - timedelta(days=1, hours=2)),
                "completed_at": _ts_to_iso(now - timedelta(days=1, hours=1))
            }
        },
        {
            "id": "RX-0985",
            "patient_info": {"name": "Sunita Das", "age": 39, "gender": "Female", "contact_id": "PAT-8985"},
            "doctor_info": {"name": "Dr. K. Nair", "registration_id": "MCI-99887"},
            "medications": [
                {"drug_name": "Azithromycin", "strength": "500mg", "frequency": "1-0-0", "duration": "3 Days", "instructions": "Before food"}
            ],
            "status": PrescriptionStatus.PICKED_UP,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 225.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(days=2, hours=5)),
                "accepted_at": _ts_to_iso(now - timedelta(days=2, hours=4)),
                "ready_at": _ts_to_iso(now - timedelta(days=2, hours=3)),
                "completed_at": _ts_to_iso(now - timedelta(days=2, hours=1))
            }
        },
        {
            "id": "RX-0980",
            "patient_info": {"name": "Gopal Menon", "age": 47, "gender": "Male", "contact_id": "PAT-8980"},
            "doctor_info": {"name": "Dr. V. Rao", "registration_id": "MCI-44556"},
            "medications": [
                {"drug_name": "Omeprazole", "strength": "20mg", "frequency": "1-0-0", "duration": "14 Days", "instructions": "Before breakfast"},
                {"drug_name": "Sucralfate", "strength": "1g", "frequency": "1-1-1", "duration": "14 Days", "instructions": "Before food"}
            ],
            "status": PrescriptionStatus.DELIVERED,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 390.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(days=2, hours=8)),
                "accepted_at": _ts_to_iso(now - timedelta(days=2, hours=7)),
                "ready_at": _ts_to_iso(now - timedelta(days=2, hours=5)),
                "completed_at": _ts_to_iso(now - timedelta(days=2, hours=3))
            }
        },
        {
            "id": "RX-0975",
            "patient_info": {"name": "Pallavi Reddy", "age": 26, "gender": "Female", "contact_id": "PAT-8975"},
            "doctor_info": {"name": "Dr. Ravi Kumar", "registration_id": "MCI-88123"},
            "medications": [
                {"drug_name": "Cetirizine", "strength": "10mg", "frequency": "0-0-1", "duration": "7 Days", "instructions": "At night"},
                {"drug_name": "Montelukast", "strength": "10mg", "frequency": "0-0-1", "duration": "14 Days", "instructions": "At night"}
            ],
            "status": PrescriptionStatus.DELIVERED,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 310.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(days=3, hours=6)),
                "accepted_at": _ts_to_iso(now - timedelta(days=3, hours=5)),
                "ready_at": _ts_to_iso(now - timedelta(days=3, hours=4)),
                "completed_at": _ts_to_iso(now - timedelta(days=3, hours=2))
            }
        },
        {
            "id": "RX-0970",
            "patient_info": {"name": "Arjun Bhat", "age": 58, "gender": "Male", "contact_id": "PAT-8970"},
            "doctor_info": {"name": "Dr. S. Gupta", "registration_id": "MCI-55678"},
            "medications": [
                {"drug_name": "Metoprolol", "strength": "50mg", "frequency": "1-0-1", "duration": "30 Days", "instructions": "With meals"},
                {"drug_name": "Clopidogrel", "strength": "75mg", "frequency": "0-1-0", "duration": "30 Days", "instructions": "After lunch"}
            ],
            "status": PrescriptionStatus.PICKED_UP,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 480.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(days=4, hours=5)),
                "accepted_at": _ts_to_iso(now - timedelta(days=4, hours=4)),
                "ready_at": _ts_to_iso(now - timedelta(days=4, hours=3)),
                "completed_at": _ts_to_iso(now - timedelta(days=4, hours=1))
            }
        },
        {
            "id": "RX-0965",
            "patient_info": {"name": "Jaya Varma", "age": 44, "gender": "Female", "contact_id": "PAT-8965"},
            "doctor_info": {"name": "Dr. Meena Iyer", "registration_id": "MCI-78432"},
            "medications": [
                {"drug_name": "Gabapentin", "strength": "300mg", "frequency": "0-0-1", "duration": "14 Days", "instructions": "At night"},
                {"drug_name": "Paracetamol", "strength": "650mg", "frequency": "1-0-1", "duration": "5 Days", "instructions": "After food"}
            ],
            "status": PrescriptionStatus.DELIVERED,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 340.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(days=5, hours=7)),
                "accepted_at": _ts_to_iso(now - timedelta(days=5, hours=6)),
                "ready_at": _ts_to_iso(now - timedelta(days=5, hours=4)),
                "completed_at": _ts_to_iso(now - timedelta(days=5, hours=2))
            }
        },
        {
            "id": "RX-0960",
            "patient_info": {"name": "Vinod Sharma", "age": 53, "gender": "Male", "contact_id": "PAT-8960"},
            "doctor_info": {"name": "Dr. Arjun Singh", "registration_id": "MCI-12903"},
            "medications": [
                {"drug_name": "Losartan", "strength": "50mg", "frequency": "1-0-0", "duration": "30 Days", "instructions": "Morning"},
                {"drug_name": "Hydrochlorothiazide", "strength": "25mg", "frequency": "1-0-0", "duration": "30 Days", "instructions": "Morning"},
                {"drug_name": "Aspirin", "strength": "75mg", "frequency": "0-1-0", "duration": "30 Days", "instructions": "After lunch"}
            ],
            "status": PrescriptionStatus.DELIVERED,
            "delivery_mode": DeliveryMode.HOME_DELIVERY,
            "total_amount": 610.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(days=6, hours=8)),
                "accepted_at": _ts_to_iso(now - timedelta(days=6, hours=7)),
                "ready_at": _ts_to_iso(now - timedelta(days=6, hours=5)),
                "completed_at": _ts_to_iso(now - timedelta(days=6, hours=3))
            }
        },

        # --- REJECTED ---
        {
            "id": "RX-1007",
            "patient_info": {"name": "Rahul Verma", "age": 22, "gender": "Male", "contact_id": "PAT-9007"},
            "doctor_info": {"name": "Dr. K. Nair", "registration_id": "MCI-99887"},
            "medications": [{"drug_name": "Unknown Drug", "strength": "???", "frequency": "1-1-1", "duration": "1 Day", "instructions": "???"}],
            "status": PrescriptionStatus.REJECTED,
            "delivery_mode": DeliveryMode.STORE_PICKUP,
            "total_amount": 0.00,
            "timestamps": {
                "created_at": _ts_to_iso(now - timedelta(hours=10)),
                "accepted_at": None,
                "ready_at": None,
                "completed_at": None
            }
        }
    ]

def get_initial_mock_inventory():
    now = _now()
    seed = [
        # Existing Items with prices
        {"id": "INV-001", "drug_name": "Amoxicillin", "strength": "500mg", "quantity": 120, "expiry_date": _ts_to_iso(now + timedelta(days=180)), "batch_number": "BTX-20260101", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 12.50},
        {"id": "INV-002", "drug_name": "Paracetamol", "strength": "650mg", "quantity": 8, "expiry_date": _ts_to_iso(now + timedelta(days=90)), "batch_number": "BTX-20251210", "threshold": 10, "is_low_stock": True, "is_expiring_soon": False, "price": 5.00},
        {"id": "INV-003", "drug_name": "Pantoprazole", "strength": "40mg", "quantity": 45, "expiry_date": _ts_to_iso(now + timedelta(days=15)), "batch_number": "BTX-20250801", "threshold": 10, "is_low_stock": False, "is_expiring_soon": True, "price": 8.75},
        {"id": "INV-004", "drug_name": "Cetirizine", "strength": "10mg", "quantity": 3, "expiry_date": _ts_to_iso(now + timedelta(days=10)), "batch_number": "BTX-20250601", "threshold": 10, "is_low_stock": True, "is_expiring_soon": True, "price": 4.00},
        {"id": "INV-005", "drug_name": "Metformin", "strength": "500mg", "quantity": 200, "expiry_date": _ts_to_iso(now + timedelta(days=365)), "batch_number": "BTX-20260715", "threshold": 20, "is_low_stock": False, "is_expiring_soon": False, "price": 6.50},
        {"id": "INV-006", "drug_name": "Ibuprofen", "strength": "400mg", "quantity": 50, "expiry_date": _ts_to_iso(now + timedelta(days=200)), "batch_number": "BTX-20260505", "threshold": 15, "is_low_stock": False, "is_expiring_soon": False, "price": 7.00},
        {"id": "INV-007", "drug_name": "Omeprazole", "strength": "20mg", "quantity": 30, "expiry_date": _ts_to_iso(now + timedelta(days=120)), "batch_number": "BTX-20260214", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 9.50},
        {"id": "INV-008", "drug_name": "Azithromycin", "strength": "500mg", "quantity": 10, "expiry_date": _ts_to_iso(now + timedelta(days=40)), "batch_number": "BTX-20250920", "threshold": 5, "is_low_stock": False, "is_expiring_soon": False, "price": 45.00},
        {"id": "INV-009", "drug_name": "Amlodipine", "strength": "5mg", "quantity": 80, "expiry_date": _ts_to_iso(now + timedelta(days=300)), "batch_number": "BTX-20260810", "threshold": 20, "is_low_stock": False, "is_expiring_soon": False, "price": 5.50},
        {"id": "INV-010", "drug_name": "Atorvastatin", "strength": "10mg", "quantity": 60, "expiry_date": _ts_to_iso(now + timedelta(days=250)), "batch_number": "BTX-20260901", "threshold": 15, "is_low_stock": False, "is_expiring_soon": False, "price": 11.00},
        {"id": "INV-011", "drug_name": "Losartan", "strength": "50mg", "quantity": 100, "expiry_date": _ts_to_iso(now + timedelta(days=330)), "batch_number": "BTX-20261022", "threshold": 20, "is_low_stock": False, "is_expiring_soon": False, "price": 8.00},
        {"id": "INV-012", "drug_name": "Gabapentin", "strength": "300mg", "quantity": 7, "expiry_date": _ts_to_iso(now + timedelta(days=25)), "batch_number": "BTX-20250915", "threshold": 10, "is_low_stock": True, "is_expiring_soon": True, "price": 15.00},
        {"id": "INV-013", "drug_name": "Hydrochlorothiazide", "strength": "25mg", "quantity": 90, "expiry_date": _ts_to_iso(now + timedelta(days=280)), "batch_number": "BTX-20261111", "threshold": 20, "is_low_stock": False, "is_expiring_soon": False, "price": 3.50},
        {"id": "INV-014", "drug_name": "Sertraline", "strength": "50mg", "quantity": 40, "expiry_date": _ts_to_iso(now + timedelta(days=150)), "batch_number": "BTX-20260404", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 18.00},
        {"id": "INV-015", "drug_name": "Simvastatin", "strength": "20mg", "quantity": 55, "expiry_date": _ts_to_iso(now + timedelta(days=190)), "batch_number": "BTX-20260318", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 10.00},
        {"id": "INV-016", "drug_name": "Levothyroxine", "strength": "100mcg", "quantity": 25, "expiry_date": _ts_to_iso(now + timedelta(days=110)), "batch_number": "BTX-20260120", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 7.50},
        {"id": "INV-017", "drug_name": "Metoprolol", "strength": "50mg", "quantity": 35, "expiry_date": _ts_to_iso(now + timedelta(days=140)), "batch_number": "BTX-20260228", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 9.00},
        {"id": "INV-018", "drug_name": "Albuterol Inhaler", "strength": "90mcg", "quantity": 12, "expiry_date": _ts_to_iso(now + timedelta(days=360)), "batch_number": "BTX-20260606", "threshold": 5, "is_low_stock": False, "is_expiring_soon": False, "price": 185.00},
        {"id": "INV-019", "drug_name": "Escitalopram", "strength": "10mg", "quantity": 4, "expiry_date": _ts_to_iso(now + timedelta(days=45)), "batch_number": "BTX-20251010", "threshold": 10, "is_low_stock": True, "is_expiring_soon": False, "price": 14.00},
        {"id": "INV-020", "drug_name": "Prednisone", "strength": "20mg", "quantity": 20, "expiry_date": _ts_to_iso(now + timedelta(days=80)), "batch_number": "BTX-20251122", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 6.00},
        {"id": "INV-021", "drug_name": "Ciprofloxacin", "strength": "500mg", "quantity": 15, "expiry_date": _ts_to_iso(now + timedelta(days=70)), "batch_number": "BTX-20251105", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 22.00},
        {"id": "INV-022", "drug_name": "Doxycycline", "strength": "100mg", "quantity": 6, "expiry_date": _ts_to_iso(now + timedelta(days=12)), "batch_number": "BTX-20250815", "threshold": 8, "is_low_stock": True, "is_expiring_soon": True, "price": 12.00},
        {"id": "INV-023", "drug_name": "Insulin Glargine", "strength": "100U/ml", "quantity": 10, "expiry_date": _ts_to_iso(now + timedelta(days=60)), "batch_number": "BTX-20251201", "threshold": 5, "is_low_stock": False, "is_expiring_soon": False, "price": 680.00},
        {"id": "INV-024", "drug_name": "Furosemide", "strength": "40mg", "quantity": 28, "expiry_date": _ts_to_iso(now + timedelta(days=100)), "batch_number": "BTX-20251215", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 4.50},
        {"id": "INV-025", "drug_name": "Clopidogrel", "strength": "75mg", "quantity": 42, "expiry_date": _ts_to_iso(now + timedelta(days=310)), "batch_number": "BTX-20260909", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 16.00},
        {"id": "INV-026", "drug_name": "Montelukast", "strength": "10mg", "quantity": 65, "expiry_date": _ts_to_iso(now + timedelta(days=220)), "batch_number": "BTX-20260520", "threshold": 15, "is_low_stock": False, "is_expiring_soon": False, "price": 12.50},
        {"id": "INV-027", "drug_name": "Aspirin", "strength": "81mg", "quantity": 150, "expiry_date": _ts_to_iso(now + timedelta(days=400)), "batch_number": "BTX-20261201", "threshold": 30, "is_low_stock": False, "is_expiring_soon": False, "price": 2.50},
        {"id": "INV-028", "drug_name": "Diazepam", "strength": "5mg", "quantity": 18, "expiry_date": _ts_to_iso(now + timedelta(days=95)), "batch_number": "BTX-20251220", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 8.00},
        {"id": "INV-029", "drug_name": "Tramadol", "strength": "50mg", "quantity": 5, "expiry_date": _ts_to_iso(now + timedelta(days=18)), "batch_number": "BTX-20250810", "threshold": 10, "is_low_stock": True, "is_expiring_soon": True, "price": 10.00},
        {"id": "INV-030", "drug_name": "Warfarin", "strength": "5mg", "quantity": 33, "expiry_date": _ts_to_iso(now + timedelta(days=160)), "batch_number": "BTX-20260305", "threshold": 10, "is_low_stock": False, "is_expiring_soon": False, "price": 7.00}
    ]
    # sorted soonest-expiry first
    seed.sort(key=lambda x: x["expiry_date"])
    return seed
