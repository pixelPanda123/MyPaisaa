from pydantic import BaseModel
from typing import Optional, List


# -----------------------------
# CREDIT REPORT
# -----------------------------

class CreditReport(BaseModel):
    credit_name: Optional[str] = None
    credit_dob: Optional[str] = None
    credit_pan: Optional[str] = None
    credit_address: Optional[str] = None
    credit_phone: Optional[str] = None
    credit_email: Optional[str] = None


# -----------------------------
# INPUT SCHEMA
# -----------------------------

class KYCRequest(BaseModel):
    id: Optional[int] = None
    customer_id: Optional[str] = None 

    # USER INPUT
    user_first_name: Optional[str] = None
    user_last_name: Optional[str] = None
    user_address: Optional[str] = None

    # AADHAAR
    aadhaar_number: Optional[str] = None
    aadhaar_name: Optional[str] = None
    aadhaar_address: Optional[str] = None
    aadhaar_dob: Optional[str] = None
    aadhaar_gender: Optional[str] = None
    aadhaar_father_name: Optional[str] = None
    aadhaar_verified: Optional[str] = None

    # PAN
    pan_number: Optional[str] = None
    pan_name: Optional[str]  = None
    pan_valid: Optional[str] = None
    pan_dob: Optional[str] = None

    # FALLBACK (legacy)
    dob: Optional[str] = None

    # CREDIT REPORT
    credit_report: Optional[CreditReport] = None

    class Config:
        extra = "allow"


# -----------------------------
# OUTPUT SCHEMA
# -----------------------------

class Issue(BaseModel):
    field: str
    message: str


class AuditCheck(BaseModel):
    name: str
    result: Optional[str]
    score: Optional[float]


class KYCAudit(BaseModel):
    checks: List[AuditCheck]
    final_score: float


class KYCResponse(BaseModel):
    status: str
    confidence_score: float
    issues: List[Issue]
    audit: KYCAudit


 