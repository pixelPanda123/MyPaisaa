from pydantic import BaseModel, Field
from typing import Optional, List


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
    isAadharverified: Optional[str]  # NOTE: string → will normalize later

    # PAN-related
    pancardno: Optional[str]
    fullname: Optional[str]  # PAN name
    panvalidity: Optional[str]
    pan_dob: Optional[str]

    #Other
    dob: Optional[str]  

    # Future-proof (if added later)
    # aadhaar_dob: Optional[str]
    # credit_report: Optional[dict]


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
    status: str  # approved / manual_review / rejected
    confidence_score: float
    issues: List[Issue]
    audit: KYCAudit