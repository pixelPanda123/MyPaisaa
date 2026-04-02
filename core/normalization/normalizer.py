from core.normalization.name_normalizer import normalize_name, build_user_full_name
from core.normalization.dob_normalizer import normalize_dob
from core.normalization.address_normalizer import normalize_address


def normalize_kyc_data(data):
    normalized = {}

    # -----------------------
    # Names
    # -----------------------

    user_full_name = build_user_full_name(data.firstname, data.lastname)

    normalized["user_name"] = normalize_name(user_full_name)
    normalized["aadhaar_name"] = normalize_name(data.nameasperaadhar)
    normalized["pan_name"] = normalize_name(data.fullname)

    # -----------------------
    # DOB
    # -----------------------

    pan_dob = data.pan_dob or data.dob  # fallback and huge problem if improperly used. 

    normalized["pan_dob"] = normalize_dob(pan_dob)
    normalized["aadhaar_dob"] = normalize_dob(data.aadhaar_dob)

    # -----------------------
    # Address
    # -----------------------

    normalized["user_address"] = normalize_address(data.currentaddress)
    normalized["aadhaar_address"] = normalize_address(data.aadhaarAddress)

    # -----------------------
    # Boolean normalization
    # -----------------------

    normalized["is_aadhaar_verified"] = str(data.isAadharverified).lower() == "true"

    # -----------------------
    # PAN
    # -----------------------

    normalized["pan"] = data.pancardno.upper() if data.pancardno else None
    normalized["pan_valid"] = (data.panvalidity or "").upper() == "VALID"

    return normalized