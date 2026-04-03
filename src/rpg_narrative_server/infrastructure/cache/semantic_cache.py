import hashlib
import logging
from typing import Any

from rpg_narrative_server.infrastructure.cache.ttl_cache import TTLCache
from rpg_narrative_server.vector_index.utils.similarity import cosine_similarity

logger = logging.getLogger("rpg_narrative_server.semantic_cache")


class SemanticCache:
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

    def _query_key(self, campaign_id: str, query: str) -> str:
        q = self._normalize(query)
        raw = f"{campaign_id}:{q}"
        return hashlib.sha1(raw.encode()).hexdigest()

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

    def get(self, campaign_id: str, query: str, vector) -> Any | None:
        if not query:
            return None

        qk = self._query_key(campaign_id, query)

        # L1
        result = self.query_cache.get(qk)
        if result is not None:
            logger.debug("[SemanticCache] L1 hit")
            return result

        # L2
        if vector is None:
            return None

        best = None
        best_score = 0.0

        for entry in self._iter_semantic_entries():
            vec = entry.get("vector")
            res = entry.get("result")

            score = self._safe_similarity(vector, vec)

            if score >= 0.999:
                self.query_cache.set(qk, res)
                return res

            if score > best_score:
                best_score = score
                best = res

        if best_score >= self.similarity_threshold:
            logger.debug(f"[SemanticCache] L2 hit ({best_score:.3f})")
            self.query_cache.set(qk, best)
            return best

        return None

    # ---------------------------------------------------------
    # insert
    # ---------------------------------------------------------

    def set(self, campaign_id: str, query: str, vector, result) -> None:
        if not query or result is None:
            return

        qk = self._query_key(campaign_id, query)

        self.query_cache.set(qk, result)

        if vector is not None:
            self.semantic_cache.set(
                qk,
                {
                    "vector": vector,
                    "result": result,
                },
            )

    # ---------------------------------------------------------
    # maintenance
    # ---------------------------------------------------------

    def clear(self):
        self.query_cache.clear()
        self.semantic_cache.clear()
