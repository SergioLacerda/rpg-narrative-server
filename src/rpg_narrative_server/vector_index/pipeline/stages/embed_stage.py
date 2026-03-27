import logging

logger = logging.getLogger("rpg_narrative_server.vector_index.embed_stage")


class EmbedStage:
    """
    Responsável por garantir que o vetor da query (q_vec) existe.

    🔥 REGRAS:
    - Só calcula embedding se não existir
    - Não sobrescreve embedding já existente
    - Fail-safe com log
    """

    def __init__(self, embedding_fn):
        self.embedding_fn = embedding_fn

    async def run(self, ctx):

        if ctx.q_vec is not None:
            return ctx

        if not ctx.query:
            logger.warning("EmbedStage: empty query")
            ctx.q_vec = []
            return ctx

        try:
            ctx.q_vec = await self.embedding_fn(ctx.query)

        except Exception:
            logger.exception("EmbedStage failed")
            raise

        return ctx