from rapidfuzz import fuzz


class CreditAnalyzer:
    """
    Evaluates the credit report as a standalone scoring source.

    This is deliberately separate from NameMatch/AddressMatch which compare
    credit fields *against* other sources. CreditAnalyzer asks a different
    question: how much does the credit report itself corroborate the identity
    being verified, based on completeness and internal cross-field consistency?

    Produces a credit_score between 0.0 and 1.0.
    """

    # Weight of each field toward the completeness score.
    # Fields that are stronger identity anchors are weighted higher.
    FIELD_WEIGHTS = {
        "credit_pan":     0.35,   # strongest anchor — unique identifier
        "credit_name":    0.30,   # high value
        "credit_dob":     0.20,   # strong corroborating field
        "credit_address": 0.15,   # useful but often inconsistent
    }

    def compute(self, data):

        # -----------------------
        # AVAILABILITY CHECK
        # -----------------------

        credit_pan     = data.get("credit_pan")
        credit_name    = data.get("credit_name")    # token list
        credit_dob     = data.get("credit_dob")     # normalized string
        credit_address = data.get("credit_address") # token list

        available = any([credit_pan, credit_name, credit_dob, credit_address])

        if not available:
            return {
                "available":         False,
                "score":             None,
                "completeness_score": None,
                "consistency_score":  None,
                "field_presence":    {},
                "consistency_checks": []
            }

        # -----------------------
        # COMPLETENESS SCORE
        # Weighted presence of each credit field.
        # -----------------------

        field_presence = {
            "credit_pan":     credit_pan     is not None,
            "credit_name":    credit_name    is not None,
            "credit_dob":     credit_dob     is not None,
            "credit_address": credit_address is not None,
        }

        completeness_score = sum(
            self.FIELD_WEIGHTS[field]
            for field, present in field_presence.items()
            if present
        )

        # -----------------------
        # CONSISTENCY SCORE
        # Cross-checks credit fields against verified document fields.
        # These are lightweight corroboration checks, not fuzzy similarity
        # scoring (that lives in NameMatch/AddressMatch).
        # Each check contributes equally to the consistency score.
        # -----------------------

        consistency_checks = []

        # Credit PAN vs document PAN — exact match expected
        pan = data.get("pan")
        if credit_pan and pan:
            pan_match = credit_pan == pan
            consistency_checks.append({
                "check":  "credit_pan_vs_pan",
                "passed": pan_match,
                "detail": None if pan_match else f"{credit_pan} != {pan}"
            })

        # Credit DOB vs PAN DOB
        pan_dob = data.get("pan_dob")
        if credit_dob and pan_dob:
            dob_match = credit_dob == pan_dob
            consistency_checks.append({
                "check":  "credit_dob_vs_pan_dob",
                "passed": dob_match,
                "detail": None if dob_match else f"{credit_dob} != {pan_dob}"
            })

        # Credit DOB vs Aadhaar DOB
        aadhaar_dob = data.get("aadhaar_dob")
        if credit_dob and aadhaar_dob:
            dob_match = credit_dob == aadhaar_dob
            consistency_checks.append({
                "check":  "credit_dob_vs_aadhaar_dob",
                "passed": dob_match,
                "detail": None if dob_match else f"{credit_dob} != {aadhaar_dob}"
            })

        # Credit name vs PAN name — fuzzy, light threshold
        pan_name = data.get("pan_name")
        if credit_name and pan_name:
            name_score = fuzz.token_sort_ratio(
                " ".join(credit_name), " ".join(pan_name)
            ) / 100.0
            consistency_checks.append({
                "check":  "credit_name_vs_pan_name",
                "passed": name_score >= 0.75,
                "detail": f"similarity={round(name_score, 3)}"
            })

        # Credit name vs Aadhaar name — fuzzy, light threshold
        aadhaar_name = data.get("aadhaar_name")
        if credit_name and aadhaar_name:
            name_score = fuzz.token_sort_ratio(
                " ".join(credit_name), " ".join(aadhaar_name)
            ) / 100.0
            consistency_checks.append({
                "check":  "credit_name_vs_aadhaar_name",
                "passed": name_score >= 0.75,
                "detail": f"similarity={round(name_score, 3)}"
            })

        if consistency_checks:
            passed_count    = sum(1 for c in consistency_checks if c["passed"])
            consistency_score = passed_count / len(consistency_checks)
        else:
            consistency_score = None

        # -----------------------
        # FINAL CREDIT SCORE
        # Completeness tells us how much data the credit report provided.
        # Consistency tells us how well it agrees with verified documents.
        # When consistency is unavailable, fall back to completeness alone.
        # -----------------------

        if consistency_score is not None:
            credit_score = 0.4 * completeness_score + 0.6 * consistency_score
        else:
            credit_score = completeness_score

        return {
            "available":          True,
            "score":              round(credit_score, 4),
            "completeness_score": round(completeness_score, 4),
            "consistency_score":  round(consistency_score, 4) if consistency_score is not None else None,
            "field_presence":     field_presence,
            "consistency_checks": consistency_checks,
        }