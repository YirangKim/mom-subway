# ai/models/faq_model.py

from ai.models.intent_model import model # SentenceTransformer
from ai.data.faq_data import FAQ_DATA
from ai.vector_db.faq_chroma_client import (
    save_faq_examples,
    search_similar_faq
)


def setup_faq_rag():
    # FAQ 질문 벡터화 후 ChromaDB 저장

    questions = []

    for item in FAQ_DATA:
        questions.append(item["question"])

    # FAQ 질문 벡터화
    embeddings = model.encode(questions).tolist()

    # FAQ 전용 ChromaDB에 저장
    save_result = save_faq_examples(embeddings)

    return {
        "message": "FAQ 미니 RAG 세팅 완료",
        "path": save_result["path"],
        "count": save_result["count"]
    }


def search_faq_tip(message: str, intent: str):
    # FAQ 미니 RAG 검색

    # 사용자 문장 벡터화
    query_embedding = model.encode(message).tolist()

    # ChromaDB에서 유사 FAQ 검색
    result = search_similar_faq(
        query_embedding=query_embedding,
        n_results=5
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    if not documents:
        return None

    # FAQ 후보 목록 생성
    # distance는 낮을수록 좋음
    # score는 높을수록 좋음

    faq_candidates = []

    for index, metadata in enumerate(metadatas):
        matched_question = documents[index]
        category = metadata.get("category")
        distance = distances[index]

        base_score = 1 / (1 + distance)

        category_bonus = 0

        if category == intent:
            category_bonus = 0.05
        elif category == "all":
            category_bonus = 0.02

        final_score = base_score + category_bonus

        faq_candidates.append({
            "title": "육아 이동 팁",
            "content": metadata.get("answer"),
            "matched_question": matched_question,
            "category": category,
            "score": round(base_score, 4),
            "distance": round(distance, 4),
            "final_score": round(final_score, 4),
            "source": "faq_mini_rag"
        })

    faq_candidates.sort(
        key=lambda item: item["final_score"],
        reverse=True
    )

    best_faq = faq_candidates[0]

    # 점수 낮으면 팁 제공 안 함
    if best_faq["score"] < 0.35:
        return None

    return {
        "title": best_faq["title"],
        "content": best_faq["content"],
        "matched_question": best_faq["matched_question"],
        "category": best_faq["category"],
        "score": best_faq["score"],
        "distance": best_faq["distance"],
        "source": best_faq["source"],
        "candidates": faq_candidates
    }