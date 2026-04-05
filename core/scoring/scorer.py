class Scorer:
    def __init__(self, checks):
        # self.identity_checks = identity_checks
        # self.credit_analyzer = credit_analyzer
        self.checks = checks    

    def compute(self, data):
        identity_results = []
        identity_weight_sum = 0.0
        identity_score_sum = 0.0

        # Identity scoring
        for check in self.checks:
            result = check.compute(data)

            score = result.get("score")
            available = result.get("available")
            weight = check.weight

            identity_results.append({
                "name": check.__class__.__name__,
                "score": score,
                "available": available,
                "weight": weight
            })

            if available and score is not None:
                identity_score_sum += weight * score
                identity_weight_sum += weight

        identity_score = (
            identity_score_sum / identity_weight_sum
            if identity_weight_sum > 0 else 0
        )

        # Credit scoring
        # credit_result = self.credit_analyzer.compute(
        #     data.get("credit_report")
        # )

        # credit_score = credit_result.get("score", 0)

        # Combine (IMPORTANT: tunable weights)
        # FINAL_IDENTITY_WEIGHT = 0.6
        # # FINAL_CREDIT_WEIGHT = 0.4

        # final_score = (
        #     FINAL_IDENTITY_WEIGHT * identity_score 
        #     # + FINAL_CREDIT_WEIGHT * credit_score
        # )
        FINAL_IDENTITY_WEIGHT = 0.6

        final_score = identity_score

        return {
            "final_score": final_score,
            "identity_score": identity_score,
            # "credit_score": credit_score,
            "identity_checks": identity_results,
            # "credit": credit_result
        }