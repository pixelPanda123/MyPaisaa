class DecisionEngine:
    def __init__(self):
        self.APPROVE_THRESHOLD        = 0.85
        self.REVIEW_THRESHOLD         = 0.65
        self.LOW_SIMILARITY_THRESHOLD = 0.75  # soft issue flag below this

    def evaluate(self, normalized_data, score_result):
        issues = []

        # =======================================================
        # BUILD AUDIT FIRST — always, unconditionally.
        # Every reject and review path below has a full audit trail.
        # Audit is now grouped by check type, not a flat list.
        # =======================================================

        # --- Identity similarity checks (NameMatch, AddressMatch) ---
        identity_checks = []
        for check in score_result.get("checks", []):
            identity_checks.append({
                "name":            check.get("name"),
                "available":       check.get("available", False),
                "score":           round(check.get("score"), 4) if check.get("score") is not None else None,
                "pairs_evaluated": check.get("pairs_evaluated", 0),
                "weight":          check.get("weight", 0.0),
            })

        # --- DOB hard check ---
        dob_result  = score_result.get("dob")
        dob_audit   = None
        if dob_result is not None:
            dob_audit = {
                "available":        dob_result.get("available", False),
                "passed":           dob_result.get("passed"),
                "pairs_evaluated":  dob_result.get("pairs_evaluated", 0),
                "mismatched_pairs": dob_result.get("mismatched_pairs", []),
            }

        # --- Credit analyzer ---
        credit_result = score_result.get("credit")
        credit_audit  = None
        if credit_result is not None:
            credit_available = credit_result.get("available", False)

            # Build consistency checks — include detail on both pass and fail
            # so the consumer can see the actual similarity score, not just pass/fail
            consistency_checks = []
            for cc in credit_result.get("consistency_checks", []):
                consistency_checks.append({
                    "check":  cc.get("check"),
                    "passed": cc.get("passed"),
                    "detail": cc.get("detail"),   # numeric similarity or mismatch detail
                })

            credit_audit = {
                "available":          credit_available,
                "score":              credit_result.get("score"),
                "completeness_score": credit_result.get("completeness_score"),
                "consistency_score":  credit_result.get("consistency_score"),
                "consistency_checks": consistency_checks,
            }

        # Pull scores needed for decisions
        final_score    = score_result.get("final_score")
        identity_score = score_result.get("identity_score")
        credit_score   = score_result.get("credit_score")

        def build_audit():
            return {
                "identity_checks": identity_checks,
                "dob":             dob_audit,
                "credit":          credit_audit,
                "final_score":     round(final_score, 4) if final_score is not None else 0.0,
                "identity_score":  round(identity_score, 4) if identity_score is not None else None,
                "credit_score":    round(credit_score, 4)   if credit_score   is not None else None,
            }

        # =======================================================
        # HARD CHECKS
        # Audit is fully built above — safe to return from here.
        # Tri-state: False = hard reject, None = unknown → manual review
        # =======================================================

        # --- PAN validity ---
        pan_valid = normalized_data.get("pan_valid")
        if pan_valid is False:
            issues.append({"field": "pan", "message": "PAN is invalid", "severity": "hard"})
            return self._reject(issues, build_audit(), final_score)
        if pan_valid is None:
            issues.append({"field": "pan", "message": "PAN validity unknown", "severity": "hard"})
            return self._manual_review(issues, build_audit(), final_score)

        # --- Aadhaar verification ---
        aadhaar_verified = normalized_data.get("aadhaar_verified")
        if aadhaar_verified is False:
            issues.append({"field": "aadhaar", "message": "Aadhaar is not verified", "severity": "hard"})
            return self._reject(issues, build_audit(), final_score)
        if aadhaar_verified is None:
            issues.append({"field": "aadhaar", "message": "Aadhaar verification status unknown", "severity": "hard"})
            return self._manual_review(issues, build_audit(), final_score)

        # --- PAN mismatch against credit report ---
        pan        = normalized_data.get("pan")
        credit_pan = normalized_data.get("credit_pan")
        if pan and credit_pan and pan != credit_pan:
            issues.append({"field": "pan", "message": "PAN mismatch between document and credit report", "severity": "hard"})
            return self._reject(issues, build_audit(), final_score)

        # --- DOB hard check ---
        if dob_result is not None and dob_result.get("available"):
            if dob_result.get("passed") is False:
                mismatched = dob_result.get("mismatched_pairs", [])
                issues.append({
                    "field":    "dob",
                    "message":  f"DOB mismatch across sources: {', '.join(mismatched)}",
                    "severity": "hard"
                })
                return self._reject(issues, build_audit(), final_score)

        # --- Credit consistency hard failures ---
        # PAN and DOB exact-match checks are hard rejects.
        # Name fuzzy checks are soft — they surface as issues but don't reject.
        if credit_result is not None and credit_result.get("available"):
            for cc in credit_result.get("consistency_checks", []):
                if not cc.get("passed") and cc.get("check") in (
                    "credit_pan_vs_pan",
                    "credit_dob_vs_pan_dob",
                    "credit_dob_vs_aadhaar_dob",
                ):
                    issues.append({
                        "field":    "credit",
                        "message":  f"Credit report hard mismatch: {cc.get('check')} — {cc.get('detail')}",
                        "severity": "hard"
                    })
                    return self._reject(issues, build_audit(), final_score)

            # Soft: failed name fuzzy checks — surface as issues but don't reject
            for cc in credit_result.get("consistency_checks", []):
                if not cc.get("passed") and cc.get("check") in (
                    "credit_name_vs_pan_name",
                    "credit_name_vs_aadhaar_name",
                ):
                    issues.append({
                        "field":    "credit",
                        "message":  f"Credit name mismatch: {cc.get('check')} — {cc.get('detail')}",
                        "severity": "soft"
                    })

        # --- Insufficient data to score ---
        if final_score is None:
            issues.append({"field": "identity", "message": "Insufficient data for identity scoring", "severity": "hard"})
            return self._manual_review(issues, build_audit(), final_score)

        # =======================================================
        # SCORE-BASED DECISION
        # =======================================================

        if final_score >= self.APPROVE_THRESHOLD:
            status = "approved"
        elif final_score >= self.REVIEW_THRESHOLD:
            status = "manual_review"
        else:
            status = "rejected"

        # =======================================================
        # SOFT ISSUES
        # =======================================================

        if final_score < self.LOW_SIMILARITY_THRESHOLD:
            issues.append({
                "field":    "identity",
                "message":  "Low similarity across documents",
                "severity": "soft"
            })

        if credit_result is None or not credit_result.get("available"):
            issues.append({
                "field":    "credit",
                "message":  "Credit report absent — scoring based on identity documents only",
                "severity": "soft"
            })

        if credit_score is None and identity_score is not None and status == "approved":
            issues.append({
                "field":    "credit",
                "message":  "Approved on identity score only — no credit report available to corroborate",
                "severity": "soft"
            })

        return {
            "status":           status,
            "confidence_score": round(final_score, 4),
            "issues":           issues,
            "audit":            build_audit()
        }

    # -----------------------
    # HELPERS
    # -----------------------

    def _reject(self, issues, audit, final_score):
        fs = round(final_score, 4) if final_score is not None else 0.0
        return {
            "status":           "rejected",
            "confidence_score": fs,
            "issues":           issues,
            "audit":            audit,
        }

    def _manual_review(self, issues, audit, final_score):
        fs = round(final_score, 4) if final_score is not None else 0.0
        return {
            "status":           "manual_review",
            "confidence_score": fs,
            "issues":           issues,
            "audit":            audit,
        }