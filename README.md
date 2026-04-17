# KYC Consistency & Identity Reconciliation System

A backend validation service that verifies identity consistency across PAN, Aadhaar, and credit report data.

---

## Prerequisites

- Python 3.9+
- pip

---

## Setup

**1. Clone the repository**
```bash
git clone <repo-url>
cd <repo-folder>
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

---

## Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

---

## Testing the Endpoint

**Endpoint:** `POST /kyc/verify`

Open `http://127.0.0.1:8000/docs` in your browser to access the Swagger UI and test directly, or use the curl command below.

**curl:**
```bash
curl -X POST http://127.0.0.1:8000/kyc/verify \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "customer_id": "CUST-001",
    "user_first_name": "Ravi",
    "user_last_name": "Kumar",
    "user_address": "Plot 12 Madhapur Hyderabad 500081",
    "aadhaar_number": "2345 6789 0123",
    "aadhaar_name": "Ravi Kumar",
    "aadhaar_address": "Plot 12 Madhapur Hyderabad 500081",
    "aadhaar_dob": "15-08-1990",
    "aadhaar_gender": "M",
    "aadhaar_father_name": "Suresh Kumar",
    "aadhaar_verified": "true",
    "pan_number": "ABCPK1234R",
    "pan_name": "Ravi Kumar",
    "pan_valid": "VALID",
    "pan_dob": "15-08-1990",
    "dob": null,
    "credit_report": {
      "credit_name": "Kumar Ravi",
      "credit_dob": "15-08-1990",
      "credit_pan": "ABCPK1234R",
      "credit_address": "Plot 12 Madhapur Hyderabad",
      "credit_phone": "9876543210",
      "credit_email": "ravi.kumar@email.com"
    }
  }'
```

**Expected response shape:**
```json
{
  "status": "approved | manual_review | rejected",
  "confidence_score": 0.0,
  "issues": [],
  "audit": {
    "identity_checks": [],
    "dob": {},
    "credit": {},
    "final_score": 0.0,
    "identity_score": 0.0,
    "credit_score": 0.0
  }
}
```

---

## Decision Logic

| Status | Condition |
|--------|-----------|
| `approved` | All hard checks pass, confidence score ≥ 0.85 |
| `manual_review` | Hard check unknown (e.g. PAN validity missing), or score between 0.65 – 0.85 |
| `rejected` | Hard check failed (invalid PAN, unverified Aadhaar, DOB mismatch, PAN mismatch), or score < 0.65 |
