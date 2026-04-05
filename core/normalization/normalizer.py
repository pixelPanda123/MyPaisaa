from core.normalization.name_normalizer import normalize_name, build_user_full_name
from core.normalization.dob_normalizer import normalize_dob
from core.normalization.address_normalizer import normalize_address


def normalize_kyc_data(data):
    normalized = {}

    # -----------------------
    # NAME
    # -----------------------

    user_full_name = build_user_full_name(
        data.user_first_name,
        data.user_last_name
    )

    normalized["user_name"] = normalize_name(user_full_name)
    normalized["aadhaar_name"] = normalize_name(data.aadhaar_name)
    normalized["pan_name"] = normalize_name(data.pan_name)

    credit_name = data.credit_report.credit_name if data.credit_report else None
    normalized["credit_name"] = normalize_name(credit_name)

    # -----------------------
    # DOB
    # -----------------------

    pan_dob = data.pan_dob or data.dob

    normalized["pan_dob"] = normalize_dob(pan_dob)
    normalized["aadhaar_dob"] = normalize_dob(data.aadhaar_dob)

    credit_dob = data.credit_report.credit_dob if data.credit_report else None
    normalized["credit_dob"] = normalize_dob(credit_dob)

    # -----------------------
    # ADDRESS
    # -----------------------

    normalized["user_address"] = normalize_address(data.user_address)
    normalized["aadhaar_address"] = normalize_address(data.aadhaar_address)

    credit_address = data.credit_report.credit_address if data.credit_report else None
    normalized["credit_address"] = normalize_address(credit_address)

    # -----------------------
    # PAN
    # -----------------------

    normalized["pan"] = data.pan_number.upper() if data.pan_number else None
    normalized["pan_valid"] = (data.pan_valid or "").upper() == "VALID"

    credit_pan = data.credit_report.credit_pan if data.credit_report else None
    normalized["credit_pan"] = credit_pan.upper() if credit_pan else None

    # -----------------------
    # AADHAAR VERIFIED
    # -----------------------

    normalized["aadhaar_verified"] = str(data.aadhaar_verified).lower() == "true"

    return normalized