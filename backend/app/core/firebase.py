import os
import json
import base64
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore, auth

# ... (Mock classes remain the same)

class MockFirestore:
    def collection(self, name):
        return MockCollection(name)

class MockCollection:
    def __init__(self, name):
        self.name = name

    def document(self, doc_id):
        return MockDocument(doc_id)

    def where(self, field, op, value):
        return self # returning self to allow chaining, though logic is limited
    
    def order_by(self, field, direction="ASCENDING"):
        return self

    def stream(self):
        return [] # Return empty list for stream

class MockDocument:
    def __init__(self, doc_id):
        self.id = doc_id
        self.exists = False # Default to not existing for safety

    def get(self):
        return self

    def to_dict(self):
        return {}

    def set(self, data):
        pass

    def update(self, data):
        pass

class FirebaseService:
    app: Optional[firebase_admin.App] = None
    db = None
    mock_mode: bool = True

    def __init__(self):
        self.initialize_firebase()

    def initialize_firebase(self):
        """
        Attempts to initialize Firebase Admin SDK.
        """
        try:
            cred = None
            
            # 1. Environment Variable
            firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
            if firebase_creds:
                try:
                    cred_dict = json.loads(firebase_creds)
                    # Basic validation to avoid 'list' attribute error
                    if isinstance(cred_dict, dict) and "type" in cred_dict:
                        cred = credentials.Certificate(cred_dict)
                    else:
                        print("Warning: FIREBASE_CREDENTIALS env var does not contain valid Service Account JSON (must be a dict).")
                except Exception as e:
                    print(f"Warning: Failed to parse FIREBASE_CREDENTIALS: {e}")

            # 2. File Path from Env
            if not cred and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if os.path.exists(path):
                    try:
                        with open(path, 'r') as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                cred = credentials.Certificate(path)
                            else:
                                print(f"Warning: File at {path} is not a valid Service Account Key.")
                    except:
                        pass

            # 3. Local File Fallback
            # Renamed to avoid conflict with 'pharmacy_credentials.json' which contains user data
            if not cred:
                potential_paths = [
                    "firebase-service-account.json",
                    "serviceAccountKey.json", 
                    "backend/firebase-service-account.json",
                    "backend/serviceAccountKey.json"
                ]
                for path in potential_paths:
                    if os.path.exists(path):
                        # Validate content before using
                        try:
                            with open(path, 'r') as f:
                                data = json.load(f)
                            
                            if isinstance(data, dict) and data.get("type") == "service_account":
                                print(f"Found local credentials at: {path}")
                                cred = credentials.Certificate(path)
                                break
                            else:
                                print(f"Skipping {path}: JSON content is not a service account key (found {type(data)}).")
                        except Exception as e:
                            print(f"Skipping {path} due to read error: {e}")

            if cred:
                self.app = firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.mock_mode = False
                print("✅ Firebase initialized successfully (REAL DB MODE)")
            else:
                print("⚠️ No Firebase credentials found. Running in MOCK MODE.")
                self.mock_mode = True
                self.db = MockFirestore()

        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {e}")
            print("⚠️ Running in MOCK MODE.")
            self.mock_mode = True
            self.db = MockFirestore()

firebase_service = FirebaseService()
