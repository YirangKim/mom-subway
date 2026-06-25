# ai_action_model.py

from ai.models.intent_model import model
from ai.data.ai_action_data import ACTION_DATA
from ai.vector_db.ai_action_chroma_client import (
    save_action_examples,
    search_similar_action
)


def make_action_document(item: dict, example: str):
    # 검색에 사용할 문장 생성

    main_keywords = ", ".join(item.get("main_keywords", []))
    sub_keywords = ", ".join(item.get("sub_keywords", []))
    request_type = item.get("request_type", "")

    return (
        f"request_type: {request_type}. "
        f"main_keywords: {main_keywords}. "
        f"sub_keywords: {sub_keywords}. "
        f"example: {example}"
    )

def setup_action_rag():
    # Action 데이터를 검색용 문장으로 만들어 저장

    documents = []
    metadatas = []

    for item in ACTION_DATA:
        for example in item.get("examples", []):
            # 키워드 + 예시 문장을 합친 검색용 문장
            document = make_action_document(item, example)

            documents.append(document)

            # 검색 결과로 돌려줄 정보
            metadatas.append({
                "priority": item.get("priority"),
                "action": item.get("action"),
                "reason": item.get("reason"),
                "request_type": item.get("request_type"),
                "main_keywords": ", ".join(item.get("main_keywords", [])),
                "sub_keywords": ", ".join(item.get("sub_keywords", [])),
                "example": example
            })

    # 검색용 문장을 임베딩
    embeddings = model.encode(documents).tolist()

    save_result = save_action_examples(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "message": "Action 추천 RAG 세팅 완료",
        "path": save_result["path"],
        "count": save_result["count"]
    }


def make_situation_text(message: str, intents: list[str], detail: dict, matches: list[dict] = None):
    # 현재 사용자 상황 문장 생성

    parts = []

    if "elevator" in intents:
        parts.append(f"엘리베이터 {detail.get('elevator_count', 0)}개 확인")

    if "dairy_room" in intents:
        parts.append(f"수유실 {detail.get('dairy_room_count', 0)}개 확인")

    if "arrival" in intents:
        parts.append(f"열차 도착정보 상태 {detail.get('arrival_status', 'unknown')}")

    if not parts:
        return "정보가 부족하거나 요청 의도가 명확하지 않은 상황."

    matched_texts = []

    if matches:
        for match in matches[:3]:
            matched_texts.append(match.get("matched_text", ""))

    matched_context = " / ".join(matched_texts)

    # multi intent는 사용자 원문만 검색에 사용
    if len(intents) > 1:
        return message

    # 단일 intent는 matched_text까지 함께 사용
    return (
        f"{message}. "
        f"{matched_context}"
    )


def search_action_recommendation(message: str, intents: list[str], detail: dict, matches: list[dict] = None):
    # 현재 상황과 유사한 action 추천 검색

    situation_text = make_situation_text(
        message=message,
        intents=intents,
        detail=detail,
        matches=matches
    )

    query_embedding = model.encode(situation_text).tolist()

    result = search_similar_action(
        query_embedding=query_embedding,
        n_results=5
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    if not documents:
        return None

    action_candidates = []

    for index, document in enumerate(documents):
        metadata = metadatas[index]
        distance = distances[index]
        score = 1 / (1 + distance)

        action_candidates.append({
            "priority": metadata.get("priority"),
            "action": metadata.get("action"),
            "reason": metadata.get("reason"),
            "request_type": metadata.get("request_type"),
            "main_keywords": metadata.get("main_keywords"),
            "sub_keywords": metadata.get("sub_keywords"),
            "matched_example": metadata.get("example"),
            "score": round(score, 4),
            "matched_situation": document
        })

    # 입력 상황 벡터화
    input_embedding = model.encode(situation_text)

    # 재정렬 후보 저장
    sorted_candidates = []

    for item in action_candidates:
        # 후보 상황 문장 가져오기
        candidate_text = item.get("matched_situation", "")

        # 후보 상황 벡터화
        candidate_embedding = model.encode(candidate_text)

        # 입력 상황과 후보 상황 유사도 계산
        similarity_score = model.similarity(
            input_embedding,
            candidate_embedding
        ).item()

        # 유사도 점수 저장
        item["similarity_score"] = round(similarity_score, 4)

        # 후보 목록에 추가
        sorted_candidates.append(item)

    # 유사도 높은 순서로 정렬
    sorted_candidates.sort(
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    # 최종 추천 후보 선택
    best_action = sorted_candidates[0]
    
    # 보조 추천 후보 선택
    second_action = None

    for item in sorted_candidates[1:]:
        # 최종 추천과 다른 action만 보조 추천으로 사용
        if item.get("action") != best_action.get("action"):
            second_action = item
            break

    # 추천 결과 반환
    return {
        # 최종 추천
        "priority": best_action.get("priority"),
        "action": best_action.get("action"),
        "reason": best_action.get("reason"),

        "sub_action": {
            "priority": second_action.get("priority"),
            "action": second_action.get("action")
        } if second_action else None,

        # 추천 점수
        "score": best_action.get("score"),
        "similarity_score": best_action.get("similarity_score"),

        # 매칭된 예시
        "matched_example": best_action.get("matched_example"),

        # 검색 입력 문장
        "input_situation": situation_text,

        # 개발 확인용 후보
        "action_candidates": sorted_candidates
    }