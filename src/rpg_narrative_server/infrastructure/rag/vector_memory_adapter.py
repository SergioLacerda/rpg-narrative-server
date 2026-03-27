import asyncio
import uuid


class VectorMemoryAdapter:

    def __init__(self, vector_index):
        self.vector_store = vector_index.vector_store
        self.embedding_service = vector_index.embedding_service

        # 🔥 stores reais do sistema
        self.document_store = vector_index.components.document_store
        self.metadata_store = vector_index.components.metadata_store

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    async def store_event(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict,
    ):
        for text in texts:

            # -------------------------------------------------
            # 1. embedding (com await seguro)
            # -------------------------------------------------
            embedding = self.embedding_service.embed(text)

            if asyncio.iscoroutine(embedding):
                embedding = await embedding

            # -------------------------------------------------
            # 2. gerar ID único
            # -------------------------------------------------
            doc_id = self._generate_id(campaign_id)

            # -------------------------------------------------
            # 3. salvar vetor
            # -------------------------------------------------
            self.vector_store.add(doc_id, embedding)

            # -------------------------------------------------
            # 4. salvar documento (texto)
            # -------------------------------------------------
            self.document_store.set(doc_id, {
                "text": text,
                "campaign_id": campaign_id,
            })

            # -------------------------------------------------
            # 5. salvar metadata
            # -------------------------------------------------
            self.metadata_store.set(doc_id, {
                **metadata,
                "campaign_id": campaign_id,
            })

    # ---------------------------------------------------------
    # INTERNAL
    # ---------------------------------------------------------

    def _generate_id(self, campaign_id: str) -> str:
        return f"{campaign_id}:{uuid.uuid4().hex}"