def get_confidence(score: float) -> str:
    """
    유사도 score를 기준으로 intent 판단 신뢰도 반환
    """

    if score >= 0.75:
        return "high"

    if score >= 0.55:
        return "medium"

    if score >= 0.45:
        return "low"

    return "unknown"


def is_unknown_confidence(confidence: str) -> bool:
    """
    unknown 여부 확인
    """

    return confidence == "unknown"