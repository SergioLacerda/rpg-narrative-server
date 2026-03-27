import heapq


class Stage2Ranker:
    """
    Refinamento intermediário:
    - lexical
    - temporal
    - cluster proximity
    """

    def __init__(self, top_k=60):
        self.top_k = top_k

    def rank(self, ctx, candidates):
        if not candidates:
            return candidates

        query_tokens = set(getattr(ctx, "query_tokens", []) or [])

        get_tokens = getattr(ctx, "get_tokens", None)
        temporal = getattr(ctx, "temporal_index", None)
        ann = getattr(ctx, "ann", None)

        heap = []

        for doc_id in candidates:
            score = 0.0

            # -----------------------------------------------------
            # lexical
            # -----------------------------------------------------
            tokens = get_tokens(doc_id) if get_tokens else []
            tokens = set(tokens or [])

            score += 0.4 * len(query_tokens & tokens)

            # -----------------------------------------------------
            # temporal
            # -----------------------------------------------------
            if temporal:
                score += 0.3 * temporal.recency_score(doc_id)

            # -----------------------------------------------------
            # cluster
            # -----------------------------------------------------
            if ann and hasattr(ann, "cluster_similarity"):
                try:
                    score += 0.3 * ann.cluster_similarity(ctx.q_vec, doc_id)
                except Exception:
                    pass

            item = (score, doc_id)

            if len(heap) < self.top_k:
                heapq.heappush(heap, item)
            else:
                heapq.heappushpop(heap, item)

        heap.sort(reverse=True)

        return [doc_id for _, doc_id in heap]
