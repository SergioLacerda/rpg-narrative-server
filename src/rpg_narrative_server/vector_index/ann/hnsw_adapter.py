# vector_index/ann/hnsw_adapter.py


class HNSWAdapter:
    """
    Adapter para integrar HNSW ao pipeline do VectorIndex.
    """

    def __init__(self, index=None):
        self.index = index

    def set_index(self, index):
        self.index = index

    def search(self, q_vec, k=20):

        if not self.index:
            return []

        results = self.index.search(q_vec, k)

        # TODO: sua implementação retorna objetos → normalizar
        return [d["id"] if isinstance(d, dict) else d for d in results]
