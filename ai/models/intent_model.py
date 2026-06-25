# ai/models/intent_model.py

# 문장을 숫자 벡터로 바꿔주는 도구 가져오기
from sentence_transformers import SentenceTransformer
# 예시 문장 목록을 가져옴
from ai.data.intent_examples import INTENT_EXAMPLES
# ChromaDB 관련 함수
from ai.vector_db.chroma_client import (
    save_intent_examples, #예시 문장 벡터를 ChromaDB에 저장하는 함수.
    search_similar_intent #사용자 문장과 비슷한 예시를 ChromaDB에서 찾는 함수.
)

from ai.utils.message_splitter import split_user_message

# 사용할 Sentence Transformer 모델
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# 모델 로드
model = SentenceTransformer(MODEL_NAME)

# 예시 문장들을 ChromaDB에 저장하기 위한 초기 세팅 함수
def setup_intent_ai():
    """
    intent 예시 문장을 벡터로 변환한 뒤 ChromaDB에 저장
    """

    texts = [] #빈 리스트를 하나 만들어. 예시 문장 모음

    # INTENT_EXAMPLES 안에 있는 데이터를 하나씩 돌면서 text만 꺼내서 texts에 담아
    for item in INTENT_EXAMPLES:
        texts.append(item["text"])

    # 문장들을 숫자 벡터로 바꿔
    # .tolist()는 그 결과를 Python 리스트 형태로 바꿔주는 거야.
    # 왜 바꾸냐면 ChromaDB에 저장하기 쉽게 만들기 위해서야.
    embeddings = model.encode(texts).tolist()

    # ChromaDB에 저장
    save_result = save_intent_examples(embeddings)

    return {
        "message": "intent AI 세팅 완료",
        "model": MODEL_NAME,
        "count": save_result["count"]
    }


# → 단일 intent용
#→ all 포함 가능
def classify_intent(message: str):
    """
    사용자 문장의 intent 분류
    """

    # 사용자 문장을 벡터로 변환
    query_embedding = model.encode(message).tolist()

    # ChromaDB에서 가장 비슷한 예시 문장 검색
    result = search_similar_intent(query_embedding)

    matched_text = result["documents"][0][0]
    matched_metadata = result["metadatas"][0][0]
    distance = result["distances"][0][0]

    intent = matched_metadata["intent"]

    # distance는 낮을수록 비슷함
    # 보기 쉽게 0~1 사이 점수로 변환
    score = 1 / (1 + distance)

    return {
        "intent": intent,
        "matched_text": matched_text,
        "score": round(score, 4),
        "distance": round(distance, 4)
    }

# → 여러 기능 실행용
#→ all 제외
#→ dairy_room / elevator / arrival만 반환
def classify_multi_intent(message: str):
    """
    사용자 문장에서 여러 intent 후보 분류
    """

    # 사용자 문장을 벡터로 변환
    query_embedding = model.encode(message).tolist()

    # 후보를 넓게 가져옴
    result = search_similar_intent(
        query_embedding=query_embedding,
        n_results=20
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    if not documents:
        return {
            "intents": [],
            "matches": []
        }

    # intent별 가장 좋은 후보만 저장
    best_by_intent = {}
    best_all_candidate = None

    for index, metadata in enumerate(metadatas):
        
        intent = metadata.get("intent")
        matched_text = documents[index]
        distance = distances[index]

        # all 후보는 바로 확장하지 않고 따로 저장
        if intent == "all":
            all_score = 1 / (1 + distance)

            all_candidate = {
                "intent": "all",
                "matched_text": matched_text,
                "score": round(all_score, 4),
                "distance": round(distance, 4)
            }

            if best_all_candidate is None:
                best_all_candidate = all_candidate
            elif all_candidate["score"] > best_all_candidate["score"]:
                best_all_candidate = all_candidate

            continue

        # distance는 낮을수록 비슷함
        score = 1 / (1 + distance)

        candidate = {
            "intent": intent,
            "matched_text": matched_text,
            "score": round(score, 4),
            "distance": round(distance, 4)
        }

        # 같은 intent 중 점수가 가장 높은 것만 남김
        if intent not in best_by_intent:
            best_by_intent[intent] = candidate
        elif candidate["score"] > best_by_intent[intent]["score"]:
            best_by_intent[intent] = candidate

    if best_all_candidate:
        best_single_score = 0

        if best_by_intent:
            best_single_score = max(
                item["score"]
                for item in best_by_intent.values()
            )

        # all 후보가 개별 intent 후보보다 충분히 강할 때만 확장
        if best_all_candidate["score"] >= 0.9 and best_all_candidate["score"] >= best_single_score + 0.03:
            for all_intent in ["dairy_room", "elevator", "arrival"]:
                best_by_intent[all_intent] = {
                    "intent": all_intent,
                    "matched_text": best_all_candidate["matched_text"],
                    "score": best_all_candidate["score"],
                    "distance": best_all_candidate["distance"]
                }

    candidates = list(best_by_intent.values())

    if not candidates:
        return {
            "intents": [],
            "matches": []
        }

    # 점수 높은 순서로 정렬
    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    best_score = candidates[0]["score"]

    intents = []
    matches = []

    for candidate in candidates:
        score = candidate["score"]

        # 기본 품질이 낮은 후보 제외
        if score < 0.86:
            continue

        # 1등과 차이가 큰 후보 제외
        if best_score - score > 0.08:
            continue

        intents.append(candidate["intent"])
        matches.append(candidate)

    return {
        "intents": intents,
        "matches": matches
    }

def classify_split_multi_intent(message: str):
    """
    split 검색 + 원문 multi 검색을 합쳐서 intent 분류
    """

    # 1. 문장을 나눔
    split_messages = split_user_message(message)

    intents = []
    matches = []

    # 2. 나눠진 문장마다 단일 intent 검색
    for split_message in split_messages:
        result = classify_intent(split_message)

        intent = result["intent"]

        # multi에서는 all 제외
        if intent == "all":
            continue

        # 중복 intent 제거
        if intent not in intents:
            intents.append(intent)

            matches.append({
                "intent": intent,
                "source_message": split_message,
                "matched_text": result["matched_text"],
                "score": result["score"],
                "distance": result["distance"],
                "source": "split_search"
            })

    # 3. 원문 전체로 multi intent 검색
    multi_result = classify_multi_intent(message)

    for match in multi_result.get("matches", []):
        intent = match["intent"]

        # multi에서는 all 제외
        if intent == "all":
            continue

        # 중복 intent 제거
        if intent not in intents:
            intents.append(intent)

            matches.append({
                "intent": intent,
                "source_message": message,
                "matched_text": match["matched_text"],
                "score": match["score"],
                "distance": match["distance"],
                "source": "multi_search"
            })

    return {
        "original_message": message,
        "split_messages": split_messages,
        "intents": intents,
        "matches": matches
    }