import logging

from rpg_narrative_server.vector_index.core.search_context import SearchContext

logger = logging.getLogger("rpg_narrative_server.retrieval.candidate")


class CandidateRetriever:

    priority = 10

    def __init__(self, embedding_fn):
        self.embed = embedding_fn

    async def run(self, ctx: SearchContext):

        if not ctx.query:
            ctx.candidates = []
            return ctx

        # -----------------------------------------
        # embedding
        # -----------------------------------------

        if ctx.q_vec is None:
            try:
                ctx.q_vec = await self.embed(ctx.query)
            except Exception:
                logger.exception("Embedding failed")
                ctx.candidates = []
                return ctx

        # -----------------------------------------
        # ANN (principal)
        # -----------------------------------------

        if ctx.ann:
            try:
                results = ctx.ann.search(ctx.q_vec, k=ctx.k)

                if results:
                    ctx.candidates = results
                    return ctx

            except Exception:
                logger.exception("ANN search failed")

        # -----------------------------------------
        # fallback (vector store)
        # -----------------------------------------

        try:
            if hasattr(ctx.vector_store, "search"):
                ctx.candidates = ctx.vector_store.search(
                    ctx.q_vec,
                    k=ctx.k
                )
                return ctx

        except Exception:
            logger.exception("Vector store fallback failed")

        # -----------------------------------------
        # último fallback (safe)
        # -----------------------------------------

        logger.warning("No retrieval strategy worked")

        ctx.candidates = []

        return ctx