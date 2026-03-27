import heapq


class Stage1Ranker:
    """
    Ranking leve (recall stage):
    - lexical overlap
    - barato
    - reduz candidatos
    """

    def __init__(self, top_k=120):
        self.top_k = top_k

    # ---------------------------------------------------------
    # core logic
    # ---------------------------------------------------------

    def rank(self, ctx, candidates):

        if not candidates:
            return candidates

        query_tokens = set(getattr(ctx, "query_tokens", []) or [])
        get_tokens = getattr(ctx, "get_tokens", None)

        heap = []

        for doc_id in candidates:

            tokens = get_tokens(doc_id) if get_tokens else []
            tokens = set(tokens or [])

            overlap = len(query_tokens & tokens)

            item = (overlap, doc_id)

            if len(heap) < self.top_k:
                heapq.heappush(heap, item)
            else:
                heapq.heappushpop(heap, item)

        heap.sort(reverse=True)

        return [doc_id for _, doc_id in heap]