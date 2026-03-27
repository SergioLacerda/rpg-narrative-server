from rpg_narrative_server.vector_index.components import VectorStore


class VectorStoreAdapter(VectorStore):

    def __init__(self, backend):
        self.backend = backend  # ex: JSONVectorStore

    def add(self, doc_id: str, vector: list[float]) -> None:
        self.backend.add(doc_id, vector)

    def get(self, doc_id: str):
        return self.backend.get(doc_id)

    def search(self, query_vector: list[float], k: int):
        return self.backend.search(query_vector, k)

    def keys(self):
        return self.backend.keys()