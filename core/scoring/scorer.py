class Scorer:
    def __init__(self, checks, dob_check=None, credit_analyzer=None):
        self.checks          = checks           # similarity checks: NameMatch, AddressMatch
        self.dob_check       = dob_check        # hard check: DOBMatch — not scored
        self.credit_analyzer = credit_analyzer  # optional: CreditAnalyzer

    # Tunable combination weights — adjust as confidence in credit data grows.
    FINAL_IDENTITY_WEIGHT = 0.6
    FINAL_CREDIT_WEIGHT   = 0.4

    def compute(self, data):

        # -----------------------
        # IDENTITY SCORING
        # Weighted average across available similarity checks.
        # -----------------------

        identity_results    = []
        identity_score_sum  = 0.0
        identity_weight_sum = 0.0

        for check in self.checks:
            result    = check.compute(data)
            score     = result.get("score")
            available = result.get("available")
            weight    = check.weight

            identity_results.append({
                "name":            check.__class__.__name__,
                "score":           score,
                "available":       available,
                "pairs_evaluated": result.get("pairs_evaluated", 0),
                "weight":          weight
            })

            if available and score is not None:
                identity_score_sum  += weight * score
                identity_weight_sum += weight

        # None when no checks had usable data — not 0.
        # 0 would cause a false rejection downstream.
        if identity_weight_sum > 0:
            identity_score     = identity_score_sum / identity_weight_sum
            identity_available = True
        else:
            identity_score     = None
            identity_available = False

        # -----------------------
        # DOB HARD CHECK
        # Not scored — passed through as-is for the decision engine.
        # -----------------------

        dob_result = None
        if self.dob_check is not None:
            dob_result = self.dob_check.compute(data)

        # -----------------------
        # CREDIT SCORING
        # -----------------------

        credit_result = None
        credit_score  = None

        if self.credit_analyzer is not None:
            credit_result = self.credit_analyzer.compute(data)
            if credit_result.get("available"):
                credit_score = credit_result.get("score")

        # -----------------------
        # FINAL SCORE
        #
        # Four combinations based on what data is available:
        #
        #   identity + credit  → weighted combination (0.6 / 0.4)
        #   identity only      → identity score as-is
        #   credit only        → credit score as-is (edge case, weak signal)
        #   neither            → None (decision engine routes to manual_review)
        # -----------------------

        if identity_score is not None and credit_score is not None:
            final_score = (
                self.FINAL_IDENTITY_WEIGHT * identity_score +
                self.FINAL_CREDIT_WEIGHT   * credit_score
            )
        elif identity_score is not None:
            final_score = identity_score
        elif credit_score is not None:
            final_score = credit_score
        else:
            final_score = None

        return {
            "final_score":        final_score,
            "identity_score":     identity_score,
            "identity_available": identity_available,
            "credit_score":       credit_score,
            "credit_available":   credit_result.get("available") if credit_result else False,
            "checks":             identity_results,
            "dob":                dob_result,
            "credit":             credit_result,
        }