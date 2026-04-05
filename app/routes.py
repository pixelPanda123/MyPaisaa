# app/routes.py

from fastapi import APIRouter
from app.schemas import KYCRequest, KYCResponse

from core.normalization.normalizer import normalize_kyc_data
from core.validation.similarity.name_match import NameMatch
from core.validation.similarity.address_match import AddressMatch
from core.scoring.scorer import Scorer
from core.decision.decision_engine import DecisionEngine


router = APIRouter()


@router.post("/kyc/verify")

def verify_kyc(request: KYCRequest):
    print("HIT")

    normalized = normalize_kyc_data(request)
    print("NORMALIZED:", normalized)

    checks = [NameMatch(), AddressMatch()]
    scorer = Scorer(checks)

    score_result = scorer.compute(normalized)
    print("SCORE RESULT:", score_result)

    decision_engine = DecisionEngine()
    result = decision_engine.evaluate(normalized, score_result)

    print("FINAL RESULT:", result)

    return result
# @router.post("/kyc/verify", response_model=KYCResponse)
# def verify_kyc(request: KYCRequest):
    
    # -----------------------
    # 1. Normalization
    # -----------------------
    normalized_data = normalize_kyc_data(request)

    # -----------------------
    # 2. Similarity Checks
    # -----------------------
    checks = [
        NameMatch(),
        AddressMatch()
    ]

    # -----------------------
    # 3. Scoring
    # -----------------------
    scorer = Scorer(checks)
    score_result = scorer.compute(normalized_data)

    # -----------------------
    # 4. Decision
    # -----------------------
    decision_engine = DecisionEngine()
    result = decision_engine.evaluate(normalized_data, score_result)

    print("FINAL RESULT:", result)

    return result