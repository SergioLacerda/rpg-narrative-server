import logging

logger = logging.getLogger("rpg_narrative_server.ann.ivf")


class IVFRouter:
    """
    Implementação simples de ANN baseada em clusters (IVF-like).
    """

    def __init__(self):
        self._index = None

    def set_index(self, index):
        """
        index deve expor:
        - search(query_vector, k)
        """
        self._index = index

    # 🔥 agora segue contrato ANN
    def search(self, query_vector: list[float], k: int = 10) -> list[str]:

        if not self._index:
            return []

        try:
            return self._index.search(query_vector, k)

        except Exception:
            logger.exception("IVF search failed")
            return []

    # ⚠️ opcional (legado)
    def route(self, query_vector: list[float]):
        if hasattr(self._index, "route"):
            return self._index.route(query_vector)
        return []
