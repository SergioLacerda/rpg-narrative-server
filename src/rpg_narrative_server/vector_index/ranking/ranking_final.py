from rpg_narrative_server.vector_index.runtime.lazy_similarity import (
    LazyVectorSimilarity,
)


class RankingFinal:
    def __init__(
        self,
        contextual_score=None,
        entity_boost=None,
        weight_base=1.0,
        weight_context=0.3,
        weight_entity=0.5,
        top_k=4,
    ):
        self.contextual_score = contextual_score
        self.entity_boost = entity_boost

        self.weight_base = weight_base
        self.weight_context = weight_context
        self.weight_entity = weight_entity

        self.top_k = top_k

    def rank(self, ctx, candidates):
        if not candidates:
            return []

        lazy = LazyVectorSimilarity(ctx.vector_store)

        base_scores = {
            doc_id: lazy.similarity(ctx.q_vec, doc_id) for doc_id in candidates
        }

        query_tokens = set(getattr(ctx, "query_tokens", []) or [])

        get_tokens = getattr(ctx, "get_tokens", None)

        docs_tokens = [
            get_tokens(doc_id) if get_tokens else [] for doc_id in candidates
        ]

        context_scores = (
            self.contextual_score.batch_score(docs_tokens)
            if self.contextual_score
            else [0.0] * len(candidates)
        )

        entity_scores = (
            self.entity_boost.batch_score(query_tokens, docs_tokens)
            if self.entity_boost
            else [0.0] * len(candidates)
        )

        results = []

        for i, doc_id in enumerate(candidates):
            final_score = (
                self.weight_base * base_scores.get(doc_id, 0.0)
                + self.weight_context * context_scores[i]
                + self.weight_entity * entity_scores[i]
            )

            results.append((final_score, doc_id))

        results.sort(reverse=True)

        return [doc_id for _, doc_id in results[: self.top_k]]
