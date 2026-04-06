# app/routes.py

from fastapi import APIRouter, HTTPException
from app.schemas import KYCRequest, KYCResponse

from core.normalization.normalizer import normalize_kyc_data
from core.validation.similarity.name_match import NameMatch
from core.validation.similarity.address_match import AddressMatch
from core.scoring.scorer import Scorer
from core.decision.decision_engine import DecisionEngine


router = APIRouter()


@router.post("/kyc/verify", response_model=KYCResponse)
async def verify_kyc(request: KYCRequest):
    print("HIT")

    # -----------------------
    # 1. Normalization
    # -----------------------
    try:
        normalized = normalize_kyc_data(request)
        print("NORMALIZED:", normalized)
    except Exception as e:
        print("NORMALIZATION ERROR:", e)
        raise HTTPException(status_code=422, detail=f"Normalization failed: {str(e)}")

    # -----------------------
    # 2. Checks + Scoring
    # -----------------------
    try:
        checks = [NameMatch(), AddressMatch()]
        scorer = Scorer(checks)
        score_result = scorer.compute(normalized)
        print("SCORE RESULT:", score_result)
    except Exception as e:
        print("SCORING ERROR:", e)
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

    # -----------------------
    # 3. Decision
    # -----------------------
    try:
        decision_engine = DecisionEngine()
        result = decision_engine.evaluate(normalized, score_result)
        print("FINAL RESULT:", result)
    except Exception as e:
        print("DECISION ERROR:", e)
        raise HTTPException(status_code=500, detail=f"Decision engine failed: {str(e)}")

    return result