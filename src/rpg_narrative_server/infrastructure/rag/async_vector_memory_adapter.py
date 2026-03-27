import asyncio
import uuid
import time


class AsyncVectorMemoryAdapter:
    def __init__(
        self,
        vector_index,
        batch_size: int = 8,
        flush_interval: float = 1.0,
    ):
        self.vector_store = vector_index.vector_store
        self.embedding_service = vector_index.embedding_service

        self.document_store = vector_index.components.document_store
        self.metadata_store = vector_index.components.metadata_store

        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self._queue = asyncio.Queue()
        self._worker_task = None
        self._running = False

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    async def start(self):
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._worker_loop())

    async def stop(self):
        self._running = False
        if self._worker_task:
            await self._worker_task

    async def store_event(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict,
    ):
        for text in texts:
            await self._queue.put((campaign_id, text, metadata))

    # ---------------------------------------------------------
    # WORKER
    # ---------------------------------------------------------

    async def _worker_loop(self):
        buffer = []
        last_flush = time.time()

        while self._running:
            try:
                item = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self.flush_interval,
                )
                buffer.append(item)

            except asyncio.TimeoutError:
                pass

            now = time.time()

            if len(buffer) >= self.batch_size or (
                buffer and now - last_flush >= self.flush_interval
            ):
                await self._flush(buffer)
                buffer.clear()
                last_flush = now

    # ---------------------------------------------------------
    # FLUSH (🔥 CORE)
    # ---------------------------------------------------------

    async def _flush(self, batch):
        if not batch:
            return

        campaign_ids = []
        texts = []
        metadatas = []

        for campaign_id, text, metadata in batch:
            campaign_ids.append(campaign_id)
            texts.append(text)
            metadatas.append(metadata)

        # -----------------------------------------------------
        # 🔥 BATCH EMBEDDING
        # -----------------------------------------------------
        embeddings = await self._embed_batch(texts)

        # -----------------------------------------------------
        # 🔥 INSERT LOOP (multi-store correto)
        # -----------------------------------------------------
        for i in range(len(texts)):
            doc_id = self._generate_id(campaign_ids[i])

            # vector
            self.vector_store.add(doc_id, embeddings[i])

            # document
            self.document_store.set(
                doc_id,
                {
                    "text": texts[i],
                    "campaign_id": campaign_ids[i],
                },
            )

            # metadata
            self.metadata_store.set(
                doc_id,
                {
                    **metadatas[i],
                    "campaign_id": campaign_ids[i],
                },
            )

    # ---------------------------------------------------------
    # EMBEDDING
    # ---------------------------------------------------------

    async def _embed_batch(self, texts):
        # se tiver suporte batch → usa
        if hasattr(self.embedding_service, "embed_batch"):
            result = self.embedding_service.embed_batch(texts)

            if asyncio.iscoroutine(result):
                return await result

            return result

        # fallback (sequencial)
        embeddings = []
        for text in texts:
            emb = self.embedding_service.embed(text)

            if asyncio.iscoroutine(emb):
                emb = await emb

            embeddings.append(emb)

        return embeddings

    # ---------------------------------------------------------
    # UTILS
    # ---------------------------------------------------------

    def _generate_id(self, campaign_id):
        return f"{campaign_id}:{uuid.uuid4().hex}"
