import re


def normalize_name(name: str):
    if not name:
        return None

    # Lowercase
    name = name.lower()

    # Remove punctuation
    name = re.sub(r"[^\w\s]", "", name)

    # Split into tokens, remove empty
    tokens = [t for t in name.split() if t]

    # NOTE: Sorting intentionally removed — order is preserved here.
    # Order-insensitive comparison is handled by token_sort_ratio in the matcher.

    return tokens


def build_user_full_name(firstname: str, lastname: str):
    if not firstname and not lastname:
        return None

    return f"{firstname or ''} {lastname or ''}".strip()