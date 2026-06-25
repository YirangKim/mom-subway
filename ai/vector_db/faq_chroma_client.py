# ai/vector_db/faq_chroma_client.py

import chromadb

from ai.data.faq_data import FAQ_DATA

CHROMA_PATH = "./ai/chroma_db/faq_cdb"
FAQ_COLLECTION_NAME = "faq_examples"

# ChromaDB 클라이언트 생성
client = chromadb.PersistentClient(path=CHROMA_PATH)


def get_faq_collection():
    # FAQ collection 가져오기
    collection = client.get_or_create_collection(
        name=FAQ_COLLECTION_NAME
    )

    return collection


def reset_faq_collection():
    # 기존 FAQ collection 삭제 후 재생성

    try:
        client.delete_collection(name=FAQ_COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=FAQ_COLLECTION_NAME
    )

    return collection


def save_faq_examples(embeddings):
    # FAQ 문서와 벡터 저장

    collection = reset_faq_collection()

    ids = []
    documents = []
    metadatas = []

    for index, item in enumerate(FAQ_DATA):
        ids.append(f"faq_{index}")

        # 검색 기준 문장
        documents.append(item["question"])

        # FAQ 부가 정보
        metadatas.append({
            "answer": item["answer"],
            "category": item["category"]
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return {
        "message": "FAQ 미니 RAG 데이터 저장 완료",
        "path": CHROMA_PATH,
        "count": len(FAQ_DATA)
    }


def search_similar_faq(query_embedding, n_results=3):
    # 사용자 문장과 비슷한 FAQ 검색

    collection = get_faq_collection()

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return result