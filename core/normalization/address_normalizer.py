import re


def normalize_address(address: str):
    if not address:
        return None

    address = address.lower()

    # Remove punctuation
    address = re.sub(r"[^\w\s]", " ", address)

    tokens = address.split()

    # Remove very common noise words
    stopwords = {"street", "road", "rd", "st", "district"}

    tokens = [t for t in tokens if t not in stopwords]

    return tokens 