from rpg_narrative_server.vector_index.builder import VectorIndexBuilder


class VectorIndexManager:
    def __init__(self, embedding_service, storage_backend, tokenizer):
        self.embedding = embedding_service
        self.storage = storage_backend
        self.tokenizer = tokenizer

        self._instances: dict[str, object] = {}

    # ---------------------------------------------------------
    # GET (lazy per campaign)
    # ---------------------------------------------------------
    def get(self, campaign_id: str):
        if campaign_id in self._instances:
            return self._instances[campaign_id]

        storage = self.storage.with_namespace(campaign_id)

        semantic_cache = self.semantic_cache_manager.get(campaign_id)

        vector_index = VectorIndexBuilder(
            embedding_service=self.embedding,
            storage_backend=storage,
            tokenizer=self.tokenizer,
        ).build(
            semantic_cache=semantic_cache,
            campaign_id=campaign_id,
        )

        self._instances[campaign_id] = vector_index

        return vector_index

    # ---------------------------------------------------------
    # OPTIONAL: cleanup
    # ---------------------------------------------------------
    def clear(self, campaign_id: str):
        instance = self._instances.pop(campaign_id, None)

        if not instance:
            return

        try:
            # -----------------------------------------------------
            # 🔥 limpeza explícita (se suportado)
            # -----------------------------------------------------
            if hasattr(instance, "close"):
                instance.close()

            if hasattr(instance, "clear"):
                instance.clear()

            # -----------------------------------------------------
            # 🔥 limpeza de componentes internos
            # -----------------------------------------------------
            components = getattr(instance, "components", None)

            if components:
                for attr in vars(components).values():
                    try:
                        if hasattr(attr, "clear"):
                            attr.clear()

                        if hasattr(attr, "close"):
                            attr.close()
                    except Exception:
                        pass

        except Exception:
            # nunca quebrar fluxo por cleanup
            pass
