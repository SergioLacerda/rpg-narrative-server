from rpg_narrative_server.vector_index.ranking.hybrid_ranker import HybridRanker


class HybridFusionStage:
    priority = 100
    min_candidates = 1

    def __init__(self, ranker=None):
        self.ranker = ranker or HybridRanker()

    async def run(self, ctx):
        candidates = ctx.candidates

        if not candidates:
            return ctx

        # ---------------------------------------------------------
        # coletar fontes
        # ---------------------------------------------------------

        sources = [candidates]
        weights = [1.0]

        # -----------------------------------------
        # lexical
        # -----------------------------------------
        lexical = getattr(ctx, "lexical_results", None)
        if lexical:
            sources.append(lexical)
            weights.append(0.8)

        # -----------------------------------------
        # causal graph
        # -----------------------------------------
        causal_graph = getattr(ctx, "causal_graph", None)

        if causal_graph:
            causal = causal_graph.expand(candidates, depth=2)
            if causal:
                sources.append(causal)
                weights.append(0.7)

        # -----------------------------------------
        # timeline
        # -----------------------------------------
        temporal = getattr(ctx, "temporal_index", None)

        if temporal:
            timeline = []

            for doc_id in candidates:
                timeline.extend(temporal.causal_chain(doc_id, depth=2))

            if timeline:
                sources.append(timeline)
                weights.append(0.6)

        # -----------------------------------------
        # memory layers
        # -----------------------------------------
        memory_layers = getattr(ctx, "memory_layers", None)

        if memory_layers:
            memory = []

            for layer in memory_layers:
                docs = layer.search(ctx.q_vec)
                if docs:
                    memory.extend(docs)

            if memory:
                sources.append(memory)
                weights.append(0.9)

        # ---------------------------------------------------------
        # deduplicação leve (🔥 importante)
        # ---------------------------------------------------------

        sources = [list(dict.fromkeys(src)) for src in sources]  # mantém ordem e remove duplicados

        # ---------------------------------------------------------
        # fusão final
        # ---------------------------------------------------------

        ctx.candidates = self.ranker.fuse(*sources, weights=weights)

        return ctx
