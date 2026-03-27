import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Optional

from rpg_narrative_server.vector_index.core.search_context import SearchContext
from rpg_narrative_server.vector_index.pipeline.builder import PipelineBuilder

logger = logging.getLogger("rpg_narrative_server.vector_index")


# ==========================================================
# PIPELINE DEPS
# ==========================================================


@dataclass
class PipelineDeps:
    vector_store: Any
    embedding_fn: Any
    memory_provider: Any
    entity_provider: Any
    context_provider: Any
    ann: Any

    temporal_index: Optional[Any] = None
    causal_graph: Optional[Any] = None
    cluster_router: Optional[Any] = None
    importance: Optional[Any] = None


# ==========================================================
# ENGINE
# ==========================================================


class VectorIndex:

    def __init__(
        self,
        components,
        embedding_service,
        tokenizer,
        memory_provider=None,
        entity_provider=None,
        context_provider=None,
    ):
        self.components = components

        self.embedding_service = embedding_service
        self.tokenizer = tokenizer

        self.vector_store = components.vector_store

        self.memory_provider = memory_provider
        self.entity_provider = entity_provider
        self.context_provider = context_provider

        self._pipeline = None
        self._pipeline_lock = asyncio.Lock()

        self._fallback_ann = None
        self._ann = None

    # ==========================================================
    # EMBEDDING (SAFE WRAPPER)
    # ==========================================================

    async def _embed(self, text: str):
        fn = self.embedding_service.embed

        result = fn(text)

        if asyncio.iscoroutine(result):
            return await result

        return result

    # ==========================================================
    # ANN RESOLUTION (CACHED)
    # ==========================================================

    def _get_ann(self):

        ann = getattr(self.components, "ann", None)
        if ann:
            return ann

        ivf = getattr(self.components, "ivf_router", None)
        if ivf:
            return ivf

        if self._fallback_ann:
            return self._fallback_ann

        if hasattr(self.vector_store, "search"):
            logger.warning("ANN not configured — using vector_store.search (slow path)")

            class VectorStoreANN:
                def __init__(self, store):
                    self.store = store

                def search(self, query_vector, k=10):
                    return self.store.search(query_vector, k)

            self._fallback_ann = VectorStoreANN(self.vector_store)
            return self._fallback_ann

        logger.error("No ANN or fallback available")
        return None

    def _resolve_ann(self):
        if self._ann is None:
            self._ann = self._get_ann()
        return self._ann

    # ==========================================================
    # CONTEXT BUILDER
    # ==========================================================

    def _build_context(self, query: str, k: int):

        tokens = self.tokenizer.tokenize(query)

        if not isinstance(tokens, list):
            tokens = [tokens]

        return SearchContext(
            query=query,
            q_vec=None,
            query_tokens=tokens,
            query_type=None,
            vector_store=self.vector_store,
            k=k,
            token_store=self.components.token_store,
            metadata_store=self.components.metadata_store,
            ann=self._resolve_ann(),
            temporal_index=getattr(self.components, "temporal_index", None),
        )

    # ==========================================================
    # PIPELINE (THREAD-SAFE LAZY INIT)
    # ==========================================================

    async def _ensure_pipeline(self):

        if self._pipeline is not None:
            return self._pipeline

        async with self._pipeline_lock:

            if self._pipeline is not None:
                return self._pipeline

            logger.info("Initializing retrieval pipeline")

            deps = PipelineDeps(
                vector_store=self.vector_store,
                embedding_fn=self._embed,
                memory_provider=self.memory_provider,
                entity_provider=self.entity_provider,
                context_provider=self.context_provider,
                ann=self._resolve_ann(),
                temporal_index=getattr(self.components, "temporal_index", None),
                causal_graph=getattr(self.components, "causal_graph", None),
                cluster_router=getattr(self.components, "cluster_router", None),
                importance=getattr(self.components, "importance", None),
            )

            self._pipeline = PipelineBuilder(deps).build()

            logger.info("Pipeline ready")

            return self._pipeline

    # ==========================================================
    # SEARCH DEBUG
    # ==========================================================

    async def search_debug(self, query: str, k: int = 4):

        if not query:
            return {
                "results": [],
                "query": query,
                "tokens": [],
            }

        logger.debug("search_debug query_len=%s k=%s", len(query), k)

        pipeline = await self._ensure_pipeline()

        if pipeline is None:
            logger.error("Pipeline not available")
            return {"results": [], "query": query, "tokens": []}

        ctx = self._build_context(query, k)
        ctx = await pipeline.run(ctx)

        return {
            "results": ctx.results or [],
            "candidates": getattr(ctx, "candidates", []),
            "query": query,
            "tokens": ctx.query_tokens,
        }

    # ==========================================================
    # SEARCH FINAL
    # ==========================================================

    async def search_async(self, query: str, k: int = 4):

        if not query:
            return []

        logger.debug("search query_len=%s k=%s", len(query), k)

        try:
            pipeline = await self._ensure_pipeline()

            if pipeline is None:
                logger.error("Pipeline not available")
                return []

            ctx = self._build_context(query, k)

            ctx = await pipeline.run(ctx)

            return ctx.results or []

        except asyncio.TimeoutError:
            logger.warning("search timeout query_len=%s", len(query))
            return []

        except Exception:
            logger.exception("search failed query_len=%s", len(query))
            return []
