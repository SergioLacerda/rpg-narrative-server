class ContextBuilder:

    def __init__(
        self,
        memory_service,
        graph_service=None,
        retrieval_service=None,
        entity_extractor=None,
        *,
        max_recent_events: int = 10,
    ):
        self.memory = memory_service
        self.graph = graph_service
        self.retrieval = retrieval_service
        self.entity_extractor = entity_extractor
        self.max_recent_events = max_recent_events

    # ---------------------------------------------------------

    async def build(
        self,
        *,
        campaign_id: str,
        action: str,
        memory=None,              # 🔥 novo (evita reload)
        history=None,
        retrieved=None,
        scene_type="DEFAULT",
    ) -> dict:

        # ----------------------------------
        # 1. MEMORY (com reuse)
        # ----------------------------------
        if memory is None:
            try:
                memory = await self.memory.load_memory(campaign_id)
            except Exception:
                memory = None

        summary = ""
        recent_events = []

        if memory:
            summary = (memory.summary or "").strip()
            recent_events = (memory.recent_events or [])[-self.max_recent_events:]

        # ----------------------------------
        # 2. ENTIDADES
        # ----------------------------------
        entities = []

        if self.entity_extractor:
            try:
                extracted = self.entity_extractor.extract(action)
                if isinstance(extracted, list):
                    entities = [e for e in extracted if isinstance(e, str)]
            except Exception:
                entities = []

        # ----------------------------------
        # 3. GRAPH
        # ----------------------------------
        related_entities = []

        if self.graph and entities:
            try:
                rel = self.graph.related(entities)

                # 🔥 dedup + limpeza
                seen = set()
                for e in rel:
                    if not isinstance(e, str):
                        continue

                    key = e.strip().lower()
                    if key and key not in seen:
                        seen.add(key)
                        related_entities.append(e.strip())

            except Exception:
                related_entities = []

        # ----------------------------------
        # 4. RETRIEVAL
        # ----------------------------------
        retrieved_context = ""

        if self.retrieval:
            try:
                result = await self.retrieval.search(
                    query=action,
                    context=summary,
                )

                if isinstance(result, str):
                    retrieved_context = result.strip()

            except Exception:
                retrieved_context = ""

        elif retrieved:
            if isinstance(retrieved, str):
                retrieved_context = retrieved.strip()
            elif isinstance(retrieved, list):
                retrieved_context = "\n".join(
                    str(x).strip() for x in retrieved if x
                )

        # ----------------------------------
        # 5. HISTORY (compat)
        # ----------------------------------
        history_context = history or []

        # ----------------------------------
        # 6. NORMALIZE SCENE
        # ----------------------------------
        scene_type = (scene_type or "DEFAULT").upper()

        # ----------------------------------
        # 7. OUTPUT FINAL
        # ----------------------------------
        return {
            "summary": summary,
            "recent_events": recent_events,
            "history": history_context,
            "retrieved": retrieved_context,
            "entities": entities,
            "related_entities": related_entities,
            "scene_type": scene_type,
        }