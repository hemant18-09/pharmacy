from typing import List, Optional
from pydantic import BaseModel, EmailStr

class PharmacySignupRequest(BaseModel):
    email: EmailStr
    password: str
    pharmacy_name: str
    license_no: str
    location: dict
