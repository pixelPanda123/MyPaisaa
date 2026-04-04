from pydantic import BaseModel
from typing import Optional, List


# -----------------------------
# CREDIT REPORT SCHEMA
# -----------------------------

class CreditReport(BaseModel):
    name: Optional[str]
    dob: Optional[str]
    pan: Optional[str]
    address: Optional[str]

    # optional extras (safe to ignore if not present)
    phone: Optional[str]
    email: Optional[str]


# -----------------------------
# INPUT SCHEMA
# -----------------------------

class KYCRequest(BaseModel):
    id: Optional[int]
    customerId: Optional[str]

    # User-entered fields
    firstname: Optional[str]
    lastname: Optional[str]
    currentaddress: Optional[str]

    # Aadhaar-related
    aadharno: Optional[str]
    nameasperaadhar: Optional[str]
    aadhaarAddress: Optional[str]
    fathername: Optional[str]
    gender: Optional[str]
    aadhar_dob: Optional[str]
    isAadharverified: Optional[str]

    # PAN-related
    pancardno: Optional[str]
    fullname: Optional[str]  # PAN name
    panvalidity: Optional[str]
    pan_dob: Optional[str]

    # fallback (legacy field)
    dob: Optional[str]

    # ✅ NEW: Credit report
    credit_report: Optional[CreditReport]


# -----------------------------
# OUTPUT SCHEMA
# -----------------------------

class Issue(BaseModel):
    field: str
    message: str


class AuditCheck(BaseModel):
    name: str
    result: Optional[str] = None
    score: Optional[float] = None


class KYCAudit(BaseModel):
    checks: List[AuditCheck]
    final_score: float


class KYCResponse(BaseModel):
    status: str
    confidence_score: float
    issues: List[Issue]
    audit: KYCAudit