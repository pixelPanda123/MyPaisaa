from pydantic import BaseModel, model_validator, Field
from typing import Optional, List, Literal


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
    aadhaar_verified: Optional[str] = None  # Inconsistent input format, normalized downstream

    # PAN
    pan_number: Optional[str] = None
    pan_name: Optional[str] = None
    pan_valid: Optional[str] = None         # Inconsistent input format, normalized downstream
    pan_dob: Optional[str] = None

    # FALLBACK (legacy)
    dob: Optional[str] = None               # Deprecated: prefer pan_dob or aadhaar_dob

    # CREDIT REPORT
    credit_report: Optional[CreditReport] = None

    @model_validator(mode="after")
    def check_at_least_one_source(self) -> "KYCRequest":
        has_aadhaar = bool(self.aadhaar_number or self.aadhaar_name)
        has_pan     = bool(self.pan_number or self.pan_name)
        has_credit  = self.credit_report is not None

        if not any([has_aadhaar, has_pan, has_credit]):
            raise ValueError(
                "At least one identity source must be present: Aadhaar, PAN, or credit report."
            )
        return self

    class Config:
        extra = "forbid"


# -----------------------------
# OUTPUT SCHEMA
# -----------------------------

class Issue(BaseModel):
    field:    str
    message:  str
    severity: Literal["hard", "soft"]   # hard = caused reject/review, soft = informational


# --- Similarity check audit (NameMatch, AddressMatch) ---
class SimilarityCheckAudit(BaseModel):
    name:            str
    available:       bool
    score:           Optional[float] = Field(default=None, ge=0.0, le=1.0)
    pairs_evaluated: int             = 0
    weight:          float


# --- DOB hard check audit ---
class DOBAudit(BaseModel):
    available:        bool
    passed:           Optional[bool]  = None   # None = no DOB data to evaluate
    pairs_evaluated:  int             = 0
    mismatched_pairs: List[str]       = []


# --- Individual credit consistency sub-check ---
class CreditConsistencyCheck(BaseModel):
    check:   str
    passed:  bool
    detail:  Optional[str] = None   # present on both pass and fail for numeric checks


# --- Credit analyzer audit ---
class CreditAudit(BaseModel):
    available:          bool
    score:              Optional[float] = Field(default=None, ge=0.0, le=1.0)
    completeness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    consistency_score:  Optional[float] = Field(default=None, ge=0.0, le=1.0)
    consistency_checks: List[CreditConsistencyCheck] = []


# --- Top-level grouped audit ---
class KYCAudit(BaseModel):
    identity_checks: List[SimilarityCheckAudit]
    dob:             Optional[DOBAudit]  = None
    credit:          Optional[CreditAudit] = None
    final_score:     float               = Field(ge=0.0, le=1.0)
    identity_score:  Optional[float]     = Field(default=None, ge=0.0, le=1.0)
    credit_score:    Optional[float]     = Field(default=None, ge=0.0, le=1.0)


class KYCResponse(BaseModel):
    status:           Literal["approved", "manual_review", "rejected"]
    confidence_score: float = Field(ge=0.0, le=1.0)
    issues:           List[Issue]
    audit:            KYCAudit