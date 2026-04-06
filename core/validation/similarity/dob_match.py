from core.validation.similarity.base import BaseCheck


class DOBMatch(BaseCheck):
    def __init__(self):
        # Weight is declared to satisfy BaseCheck contract,
        # but DOB is a hard check — it does not contribute to the similarity score.
        super().__init__(weight=0.0)

    def compare_two(self, dob1, dob2):
        """Returns True if both DOBs are present and equal, False if present but mismatched,
        None if either is missing."""
        if not dob1 or not dob2:
            return None

        return dob1 == dob2

    def compute(self, data):
        pairs = [
            ("pan_vs_aadhaar",  data.get("pan_dob"),     data.get("aadhaar_dob")),
            ("pan_vs_credit",   data.get("pan_dob"),     data.get("credit_dob")),
            ("aadhaar_vs_credit", data.get("aadhaar_dob"), data.get("credit_dob")),
        ]

        results = []
        pairs_evaluated = 0

        for label, d1, d2 in pairs:
            match = self.compare_two(d1, d2)
            if match is not None:
                pairs_evaluated += 1
                results.append({
                    "pair": label,
                    "match": match
                })

        if not results:
            # No DOB data available across any source — cannot hard check.
            return {
                "available": False,
                "passed": None,
                "pairs_evaluated": 0,
                "mismatched_pairs": []
            }

        mismatched = [r["pair"] for r in results if not r["match"]]

        return {
            "available": True,
            # passed = True only if every evaluated pair matched.
            # Any single mismatch fails the hard check.
            "passed": len(mismatched) == 0,
            "pairs_evaluated": pairs_evaluated,
            "mismatched_pairs": mismatched
        }