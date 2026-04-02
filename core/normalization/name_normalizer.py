import re


def normalize_name(name: str):
    if not name:
        return None

    # Lowercase
    name = name.lower()

    # Remove punctuation
    name = re.sub(r"[^\w\s]", "", name)

    # Split into tokens
    tokens = name.split()

    # Remove empty tokens
    tokens = [t for t in tokens if t]

    # Sort tokens (handles order differences)
    tokens.sort()

    return tokens


def build_user_full_name(firstname: str, lastname: str):
    if not firstname and not lastname:
        return None

    return f"{firstname or ''} {lastname or ''}".strip()