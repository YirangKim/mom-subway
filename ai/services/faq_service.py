# ai/services/faq_service.py

from ai.models.faq_model import search_faq_tip


def get_faq_tip(message: str, intent: str):
    # FAQ 미니 RAG 팁 조회

    faq_result = search_faq_tip(
        message=message,
        intent=intent
    )

    if faq_result is None:
        return None

    return {
        "title": faq_result["title"],
        "content": faq_result["content"],
        "matched_question": faq_result["matched_question"],
        "category": faq_result["category"],
        "score": faq_result["score"],
        "distance": faq_result["distance"],
        "source": faq_result["source"],
        "candidates": faq_result.get("candidates", []) #debug
    }
