from typing import List

from rpg_narrative_server.application.ports.storage import VectorStorePort


class ChromaVectorStore(VectorStorePort):
    def __init__(self, collection):
        self.collection = collection

    def add(self, doc_id: str, vector: List[float]) -> None:
        self.collection.add(
            ids=[doc_id],
            embeddings=[vector],
        )

    def get(self, doc_id: str) -> List[float] | None:
        result = self.collection.get(ids=[doc_id])

        if not result or not result.get("embeddings"):
            return None

        return result["embeddings"][0]

    def keys(self) -> List[str]:
        result = self.collection.get()

        if not result or not result.get("ids"):
            return []

        return result["ids"]

    def search(self, query_vector: List[float], k: int) -> List[str]:
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k,
        )

        return results["ids"][0] if results.get("ids") else []

    def clear(self) -> None:
        self.collection.delete(where={})
