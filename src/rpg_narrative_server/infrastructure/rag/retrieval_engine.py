import asyncio


class RetrievalEngine:
    """
    Infra pura: executa busca vetorial com cache, deduplicação,
    hedging e execução controlada via executor.
    """

    def __init__(
        self,
        vector_index,
        embedding_cache,
        semantic_cache,
        vector_index_factory=None,
        executor=None,
        enable_hedging=False,
        hedge_delay=0.01,
    ):
        self.default_index = vector_index
        self.vector_index_factory = vector_index_factory

        self.embedding_cache = embedding_cache
        self.semantic_cache = semantic_cache

        self.executor = executor

        self.indexes = {}
        self._inflight = {}

        self.enable_hedging = enable_hedging
        self.hedge_delay = hedge_delay

    # ---------------------------------------------------------
    # index
    # ---------------------------------------------------------

    def _get_index(self, campaign_id):

        if campaign_id is None:
            return self.default_index

        if campaign_id in self.indexes:
            return self.indexes[campaign_id]

        if not self.vector_index_factory:
            return self.default_index

        index = self.vector_index_factory(campaign_id)
        self.indexes[campaign_id] = index

        return index

    # ---------------------------------------------------------
    # embedding
    # ---------------------------------------------------------

    async def _get_embedding(self, query):
        return await self.embedding_cache.get(query)

    # ---------------------------------------------------------
    # execution helper (🔥 novo)
    # ---------------------------------------------------------

    async def _execute_index(self, index, query, q_vec, k):

        if asyncio.iscoroutinefunction(index.search):
            return await index.search(query, q_vec, k)

        if self.executor:
            return await self.executor.run_async(
                index.search,
                query,
                q_vec,
                k,
            )

        return index.search(query, q_vec, k)

    # ---------------------------------------------------------
    # hedging
    # ---------------------------------------------------------

    async def _hedged_search(self, index, query, q_vec, k):

        async def primary():
            return await self._execute_index(index, query, q_vec, k)

        async def secondary():
            await asyncio.sleep(self.hedge_delay)
            return await self._execute_index(index, query, q_vec, k)

        task1 = asyncio.create_task(primary())
        task2 = asyncio.create_task(secondary())

        done, pending = await asyncio.wait(
            [task1, task2],
            return_when=asyncio.FIRST_COMPLETED,
        )

        result = list(done)[0].result()

        # cancela com segurança
        for t in pending:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass

        return result

    # ---------------------------------------------------------
    # search
    # ---------------------------------------------------------

    async def search(self, query, k=4, campaign_id=None):

        index = self._get_index(campaign_id)

        q_vec = await self._get_embedding(query)

        cached = self.semantic_cache.get(query, q_vec)
        if cached:
            return cached

        inflight_key = (query, campaign_id, k)

        if inflight_key in self._inflight:
            return await self._inflight[inflight_key]

        async def _execute():

            try:
                # -----------------------------------------
                # search
                # -----------------------------------------
                if self.enable_hedging:
                    results = await self._hedged_search(index, query, q_vec, k)
                else:
                    results = await self._execute_index(index, query, q_vec, k)

                # -----------------------------------------
                # cache
                # -----------------------------------------
                self.semantic_cache.set(query, q_vec, results)

                return results

            except Exception:
                # evita cache inconsistente
                raise

        task = asyncio.create_task(_execute())
        self._inflight[inflight_key] = task

        try:
            return await task
        finally:
            self._inflight.pop(inflight_key, None)
