from rapidfuzz import fuzz
from core.validation.similarity.base import BaseCheck


class AddressMatch(BaseCheck):
    def __init__(self):
        super().__init__(weight=0.3)

    def compute(self, data):
        addr1 = data.get("user_address")
        addr2 = data.get("aadhaar_address")

        if not addr1 or not addr2:
            return {
                "score": None,
                "available": False
            }

        addr1_str = " ".join(addr1)
        addr2_str = " ".join(addr2)

        score = fuzz.token_sort_ratio(addr1_str, addr2_str) / 100.0

        return {
            "score": score,
            "available": True
        }