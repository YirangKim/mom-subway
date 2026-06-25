# ai_action_chroma_client.py
# ChromaDB 저장/검색 담당
# 받은 데이터를 ChromaDB에 넣고 꺼내기만 함
# 데이터 준비는 ai_action_model.py에서 담당함.

import chromadb

CHROMA_PATH = "./ai/chroma_db/ai_action_cdb"
COLLECTION_NAME = "ai_action_data"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

# collection 연결
collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

# ai_action_model.py가 만든 documents, embeddings, metadatas를 받아서 저장만 함.
# 역할이 단순해지고, main_keywords / sub_keywords / request_type 같은 새 데이터도 저장 가능해짐.
def save_action_examples(
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict]
):
    # 전달받은 데이터를 ChromaDB에 저장

    ids = [
        f"action_{index}"
        for index in range(len(documents))
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "path": CHROMA_PATH,
        "count": len(ids)
    }


def search_similar_action(query_embedding: list[float], n_results: int = 3):
    # ChromaDB에서 비슷한 action 검색

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return result