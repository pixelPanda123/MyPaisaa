from datetime import datetime


def normalize_dob(dob: str):
    if not dob:
        return None

    formats = [
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m-%d-%Y"
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(dob, fmt)
            return parsed.strftime("%Y-%m-%d")
        except:
            continue

    return None  # if all parsing fails