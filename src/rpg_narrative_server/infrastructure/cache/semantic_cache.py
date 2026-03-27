import hashlib
import logging
from typing import Any, Optional

from rpg_narrative_server.vector_index.utils.similarity import cosine_similarity

from rpg_narrative_server.infrastructure.cache.ttl_cache import TTLCache


logger = logging.getLogger("rpg_narrative_server.semantic_cache")


class SemanticCache:
    """
    Cache híbrido:

    L1 → cache por query exata (hash)
    L2 → cache por similaridade semântica (vetores)

    Estratégias:
    - promoção L2 → L1
    - early exit
    - validação de vetor
    """

    def __init__(
        self,
        size: int = 256,
        ttl: int = 1800,
        similarity_threshold: float = 0.92,
    ):
        self.size = size
        self.similarity_threshold = similarity_threshold

        self.query_cache = TTLCache(ttl=ttl, max_items=size)
        self.semantic_cache = TTLCache(ttl=ttl, max_items=size)

    # ---------------------------------------------------------
    # utils
    # ---------------------------------------------------------

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def _query_key(self, query: str) -> str:
        q = self._normalize(query)
        return hashlib.sha1(q.encode()).hexdigest()

    def _safe_similarity(self, v1, v2) -> float:
        try:
            if v1 is None or v2 is None:
                return 0.0

            if len(v1) != len(v2):
                return 0.0

            return cosine_similarity(v1, v2)

        except Exception as e:
            logger.debug(f"[SemanticCache] similarity error: {e}")
            return 0.0

    def _iter_semantic_entries(self):

        for _, value in self.semantic_cache.items():
            if value:
                yield value

    # ---------------------------------------------------------
    # lookup
    # ---------------------------------------------------------

    def get(self, query: str, vector) -> Optional[Any]:

        if not query:
            return None

        qk = self._query_key(query)

        # -----------------------------------
        # L1: exact match
        # -----------------------------------

        result = self.query_cache.get(qk)

        if result is not None:
            logger.debug("[SemanticCache] L1 hit")
            return result

        # -----------------------------------
        # L2: semantic search
        # -----------------------------------

        if vector is None:
            return None

        best = None
        best_score = 0.0

        for entry in self._iter_semantic_entries():

            vec = entry.get("vector")
            res = entry.get("result")

            score = self._safe_similarity(vector, vec)

            # early exit (ótimo match)
            if score >= 0.999:
                logger.debug("[SemanticCache] early exit (perfect match)")
                self.query_cache.set(qk, res)
                return res

            if score > best_score:
                best_score = score
                best = res

        if best_score >= self.similarity_threshold:
            logger.debug(f"[SemanticCache] L2 hit (score={best_score:.3f})")

            # 🔥 promoção L2 → L1
            self.query_cache.set(qk, best)

            return best

        return None

    # ---------------------------------------------------------
    # insert
    # ---------------------------------------------------------

    def set(self, query: str, vector, result) -> None:

        if not query or result is None:
            return

        qk = self._query_key(query)

        # L1
        self.query_cache.set(qk, result)

        # L2 (somente se vetor válido)
        if vector is not None:
            self.semantic_cache.set(
                qk,
                {
                    "vector": vector,
                    "result": result,
                }
            )

    # ---------------------------------------------------------
    # extras
    # ---------------------------------------------------------

    def invalidate(self, query: str) -> None:
        """
        Remove entrada específica
        """
        qk = self._query_key(query)

        try:
            self.query_cache.delete(qk)
            self.semantic_cache.delete(qk)
        except Exception:
            pass

    def clear(self) -> None:
        """
        Limpa todo cache
        """
        self.query_cache.clear()
        self.semantic_cache.clear()

    def stats(self) -> dict:
        """
        Debug / observabilidade
        """
        return {
            "l1_size": len(getattr(self.query_cache, "_data", {})),
            "l2_size": len(getattr(self.semantic_cache, "_data", {})),
            "threshold": self.similarity_threshold,
        }