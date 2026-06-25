# ai_action_service.py

from ai.models.ai_action_model import search_action_recommendation

# 용자 요청을 single-intent와 multi-intent로 분류
def make_action_search_context(message: str, intents: list[str], detail: dict):
    # Action RAG 검색 품질을 높이기 위한 검색용 context 생성

    intent_count = len(intents)

    if intent_count == 1:
        request_type = "single_intent"
        request_description = "사용자가 하나의 기능만 요청한 상황"
    else:
        request_type = "multi_intent"
        request_description = "사용자가 두 개 이상의 기능을 함께 요청한 상황"

    return {
        "search_message": f"""
        요청 유형: {request_type}
        상황 설명: {request_description}
        감지된 intents: {", ".join(intents)}
        사용자 원문: {message}
        상황 detail: {detail}
        """.strip(),
                "request_type": request_type
    }

def get_action_recommendation(message: str, intents: list[str], detail: dict, matches: list[dict] = None):
    # AI action 추천

    if not intents:
        return {
            "priority": "clarify_needed",
            "action": "수유실, 엘리베이터, 열차 도착정보 중 필요한 정보를 다시 선택하세요.",
            "reason": "요청이 명확해야 상황에 맞는 이동 안내를 제공할 수 있습니다.",
            "score": 0,
            "matched_situation": None,
            "input_situation": "요청 의도가 명확하지 않은 상황."
        }

    # action 추천 검색
    search_context = make_action_search_context(
    message=message,
    intents=intents,
    detail=detail
    )

    recommendation = search_action_recommendation(
        message=search_context["search_message"],
        intents=intents,
        detail=detail,
        matches=matches
    )

    # 검색 결과 없을 때 기본 응답
    if recommendation is None:
        return {
            "priority": "no_recommendation",
            "action": "현재 상황에 맞는 추천 행동을 찾지 못했어요.",
            "reason": "Action ChromaDB 검색 결과가 비어 있어 기본 안내를 반환합니다.",
            "score": 0,
            "similarity_score": 0,
            "matched_situation": None,
            "input_situation": None,
            "candidates": []
        }

    # 추천 결과 반환
    return recommendation