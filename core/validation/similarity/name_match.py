from rapidfuzz import fuzz
from core.validation.similarity.base import BaseCheck


class NameMatch(BaseCheck):
    def __init__(self):
        super().__init__(weight=0.7)

    def compare_two(self, tokens1, tokens2):
        if not tokens1 or not tokens2:
            return None

        name1 = " ".join(tokens1)
        name2 = " ".join(tokens2)

        score = fuzz.token_sort_ratio(name1, name2) / 100.0
        return score

    def compute(self, data):
        scores = []

        pairs = [
            (data["user_name"], data["aadhaar_name"]),
            (data["user_name"], data["pan_name"]),
            (data["pan_name"], data["aadhaar_name"]),
        ]

        for t1, t2 in pairs:
            score = self.compare_two(t1, t2)
            if score is not None:
                scores.append(score)

        if not scores:
            return {
                "score": None,
                "available": False
            }

        avg_score = sum(scores) / len(scores)

        return {
            "score": avg_score,
            "available": True
        }