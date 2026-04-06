from rapidfuzz import fuzz
from core.validation.similarity.base import BaseCheck


class AddressMatch(BaseCheck):
    def __init__(self):
        super().__init__(weight=0.3)

    def compare_two(self, addr1, addr2):
        if not addr1 or not addr2:
            return None

        addr1_str = " ".join(addr1)
        addr2_str = " ".join(addr2)

        # token_set_ratio: better for addresses than token_sort_ratio.
        # Handles containment well — e.g. a short address that is a subset
        # of a longer one still scores high if the tokens overlap.
        return fuzz.token_set_ratio(addr1_str, addr2_str) / 100.0

    def compute(self, data):
        scores = []

        pairs = [
            (data["user_address"],    data["aadhaar_address"]),
            (data["user_address"],    data["credit_address"]),
            (data["aadhaar_address"], data["credit_address"]),
            # No pan_address: PAN document does not carry an address field.
        ]

        pairs_evaluated = 0

        for a1, a2 in pairs:
            score = self.compare_two(a1, a2)
            if score is not None:
                scores.append(score)
                pairs_evaluated += 1

        if not scores:
            return {
                "score": None,
                "available": False,
                "pairs_evaluated": 0
            }

        avg_score = sum(scores) / len(scores)

        return {
            "score": avg_score,
            "available": True,
            "pairs_evaluated": pairs_evaluated
        }

# from rapidfuzz import fuzz
# from core.validation.similarity.base import BaseCheck


# class AddressMatch(BaseCheck):
#     def __init__(self):
#         super().__init__(weight=0.3)

#     def compare_two(self, addr1, addr2):
#         if not addr1 or not addr2:
#             return None

#         addr1_str = " ".join(addr1)
#         addr2_str = " ".join(addr2)

#         return fuzz.token_sort_ratio(addr1_str, addr2_str) / 100.0

#     def compute(self, data):
#         scores = []

#         pairs = [
#             (data["user_address"], data["aadhaar_address"]),

#             # NEW: credit comparisons
#             (data["user_address"], data["credit_address"]),
#             (data["aadhaar_address"], data["credit_address"]),
#         ]

#         for a1, a2 in pairs:
#             score = self.compare_two(a1, a2)
#             if score is not None:
#                 scores.append(score)

#         if not scores:
#             return {
#                 "score": None,
#                 "available": False
#             }

#         avg_score = sum(scores) / len(scores)

#         return {
#             "score": avg_score,
#             "available": True
#         }