import re


# Basic abbreviation expansion for Indian addresses.
# Expand before tokenizing so stopword removal and matching work correctly.
# TODO: grow this map as new patterns are observed in production data.
ABBREVIATION_MAP = {
    "apt":   "apartment",
    "appt":  "apartment",
    "soc":   "society",
    "sec":   "sector",
    "hyd":   "hyderabad",
    "blr":   "bangalore",
    "mum":   "mumbai",
    "del":   "delhi",
    "hno":   "house",
    "h no":  "house",
    "no":    "number",
    "flr":   "floor",
    "fl":    "floor",
    "plt":   "plot",
}

STOPWORDS = {
    "street", "road", "rd", "st", "district",
    "colony", "sector", "phase",
    "near", "opp", "opposite", "behind",
}


def _expand_abbreviations(address: str) -> str:
    for abbr, full in ABBREVIATION_MAP.items():
        # Match whole word only, case-insensitive already handled upstream
        address = re.sub(rf"\b{re.escape(abbr)}\b", full, address)
    return address


def normalize_address(address: str):
    if not address:
        return None

    address = address.lower()

    # Expand abbreviations before anything else
    address = _expand_abbreviations(address)

    # Remove punctuation (preserve spaces)
    address = re.sub(r"[^\w\s]", " ", address)

    tokens = address.split()

    # Separate numeric tokens (house numbers, PINs) from text tokens.
    # Both are kept — numeric tokens should be matched exactly downstream,
    # text tokens can tolerate fuzzy matching.
    numeric_tokens = [t for t in tokens if t.isdigit()]
    text_tokens = [t for t in tokens if not t.isdigit() and t not in STOPWORDS]

    # Return combined: text tokens first, numerics appended at end.
    # Matcher is responsible for treating them differently if needed.
    return text_tokens + numeric_tokens