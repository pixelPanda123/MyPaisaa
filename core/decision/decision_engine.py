class DecisionEngine:
    def __init__(self):
        self.APPROVE_THRESHOLD = 0.85
        self.REVIEW_THRESHOLD = 0.65

    def evaluate(self, normalized_data, score_result):
        issues = []
        audit_checks = []
        for check in score_result.get("checks", []):
            audit_checks.append({
                "name": check.get("name"),
                "score": check.get("score"),
                "result": "computed"
            })

        # -----------------------
        # HARD CHECKS
        # -----------------------

        # PAN validity
        if not normalized_data.get("pan_valid"):
            issues.append({
                "field": "pan",
                "message": "PAN is invalid"
            })
            return self._reject(issues, audit_checks)

        # Aadhaar verification
        if not normalized_data.get("aadhaar_verified"):
            issues.append({
                "field": "Aadhaar",
                "message": "Aadhaar not verified"
            })
            return self._reject(issues, audit_checks)

        # PAN mismatch (if credit PAN exists)
        pan = normalized_data.get("pan")
        credit_pan = normalized_data.get("credit_pan")

        if pan and credit_pan and pan != credit_pan:
            issues.append({
                "field": "pan",
                "message": "PAN mismatch between document and credit report"
            })
            return self._reject(issues, audit_checks)

        # -----------------------
        # SCORE-BASED DECISION
        # -----------------------

        final_score = score_result.get("final_score", 0)

        # Add similarity checks to audit
        for check in score_result.get("checks", []):
            audit_checks.append({
                "name": check["name"],
                "score": check["score"]
            })

        # Decision logic
        if final_score >= self.APPROVE_THRESHOLD:
            status = "approved"
        elif final_score >= self.REVIEW_THRESHOLD:
            status = "manual_review"
        else:
            status = "rejected"

        # -----------------------
        # SOFT ISSUES (optional flags)
        # -----------------------

        if final_score < 0.75:
            issues.append({
                "field": "identity",
                "message": "Low similarity across documents"
            })

        return {
            "status": status,
            "confidence_score": final_score,
            "issues": issues,
            "audit": {
                "checks": audit_checks,
                "final_score": final_score
            }
        }

    def _reject(self, issues, audit_checks):
        return {
            "status": "rejected",
            "confidence_score": 0.0,
            "issues": issues,
            "audit": {
                "checks": audit_checks,
                "final_score": 0.0
            }
        }