# ai/vector_db/chroma_client.py
# 저장 요청 : ChromaDB에 문장 + intent + 벡터 저장

import chromadb

from ai.data.intent_examples import INTENT_EXAMPLES

CHROMA_PATH = "./ai/chroma_db/intent_cdb"
COLLECTION_NAME = "intent_examples"

# ChromaDB 클라이언트 생성
client = chromadb.PersistentClient(path=CHROMA_PATH)


def get_intent_collection():
    """
    intent 예시 문장을 저장할 collection 가져오기
    없으면 새로 생성
    """

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


def reset_intent_collection():
    """
    기존 intent collection 삭제 후 다시 생성
    예시 문장을 새로 저장할 때 사용
    """

    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    return collection


def save_intent_examples(embeddings):
    """
    intent 예시 문장과 임베딩 벡터를 ChromaDB에 저장
    """

    collection = reset_intent_collection()

    ids = []
    documents = []
    metadatas = []

    for index, item in enumerate(INTENT_EXAMPLES):
        ids.append(f"intent_{index}")
        documents.append(item["text"])
        metadatas.append({
            "intent": item["intent"]
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return {
        "message": "intent 예시 문장 저장 완료",
        "count": len(INTENT_EXAMPLES)
    }

# n_results=5 가장 비슷한 예시 문장 5개를 가져옴
def search_similar_intent(query_embedding, n_results=5):
    """
    사용자 문장과 가장 비슷한 intent 예시 문장 검색
    """

    collection = get_intent_collection()

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return result