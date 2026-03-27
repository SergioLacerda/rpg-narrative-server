import logging

from rpg_narrative_server.vector_index.core.vector_index import VectorIndex
from rpg_narrative_server.vector_index.components import VectorIndexComponents

# ranking
from rpg_narrative_server.vector_index.ranking.stage1_ranker import Stage1Ranker
from rpg_narrative_server.vector_index.ranking.stage2_ranker import Stage2Ranker

# clustering
from rpg_narrative_server.vector_index.clustering.cluster_builder import ClusterBuilder
from rpg_narrative_server.vector_index.clustering.cluster_manager import ClusterManager
from rpg_narrative_server.vector_index.clustering.cluster_router import ClusterRouter

# ANN
from rpg_narrative_server.vector_index.ann.ivf_builder import IVFBuilder
from rpg_narrative_server.vector_index.ann.ivf_router import IVFRouter

# indexing
# from rpg_narrative_server.vector_index.indexing.embedding_indexer import EmbeddingIndexer

# narrativa
from rpg_narrative_server.vector_index.narrative.timeline_index import TimelineIndex
from rpg_narrative_server.vector_index.narrative.causality_graph import CausalityGraph

# classifier
from rpg_narrative_server.vector_index.classifiers.default_query_classifier import DefaultQueryClassifier

logger = logging.getLogger("rpg_narrative_server.vector_index.builder")

class VectorIndexBuilder:

    def __init__(
        self,
        embedding_service,
        storage_backend,
        tokenizer,
        memory_provider=None,
        entity_provider=None,
        context_provider=None,
        query_classifier=None,
    ):

        self.embedding = embedding_service
        self.storage = storage_backend
        self.tokenizer = tokenizer

        self.memory_provider = memory_provider
        self.entity_provider = entity_provider
        self.context_provider = context_provider
        self.query_classifier = query_classifier

    # ---------------------------------------------------------
    # ANN build (rebuildable)
    # ---------------------------------------------------------

    def _build_ann_index(self, components):

        vector_store = components.vector_store

        if not hasattr(vector_store, "keys"):
            return

        logger.info("vector_store.keys() - Storage keys: %s", vector_store.keys())
        doc_ids = vector_store.keys()

        if not doc_ids:
            return

        ivf_index = components.ivf_builder.build(
            doc_ids,
            vector_store,
        )

        if ivf_index:
            components.ivf_router.set_index(ivf_index)

    # ---------------------------------------------------------
    # clustering build
    # ---------------------------------------------------------

    def _build_clusters(self, components):

        vector_store = components.vector_store

        if not hasattr(vector_store, "keys"):
            return

        doc_ids = vector_store.keys()

        if not doc_ids:
            return

        components.cluster_manager.update(doc_ids, vector_store)

    # ---------------------------------------------------------
    # build
    # ---------------------------------------------------------

    def build(self):

        # -----------------------------------------
        # stores
        # -----------------------------------------

        vector_store = self.storage.build_vector_store()
        document_store = self.storage.build_document_store()
        token_store = self.storage.build_token_store()
        metadata_store = self.storage.build_metadata_store()

        # -----------------------------------------
        # ANN
        # -----------------------------------------

        ivf_builder = IVFBuilder()
        ivf_router = IVFRouter()

        # -----------------------------------------
        # clustering
        # -----------------------------------------

        cluster_builder = ClusterBuilder()
        cluster_manager = ClusterManager(cluster_builder)
        cluster_router = ClusterRouter(cluster_manager)

        # -----------------------------------------
        # narrativa
        # -----------------------------------------

        temporal_index = TimelineIndex()
        causal_graph = CausalityGraph()

        # -----------------------------------------
        # components
        # -----------------------------------------

        components = VectorIndexComponents(
            query_classifier=DefaultQueryClassifier(),

            stage1_ranker=Stage1Ranker(),
            stage2_ranker=Stage2Ranker(),

            cluster_manager=cluster_manager,

            vector_store=vector_store,
            document_store=document_store,
            token_store=token_store,
            metadata_store=metadata_store,

            ivf_builder=ivf_builder,
            ivf_router=ivf_router,

            temporal_index=temporal_index,
            causal_graph=causal_graph,
        )

        # extensões opcionais
        components.cluster_router = cluster_router

        components.validate()

        # -----------------------------------------
        # indexer
        # -----------------------------------------

        # embedding_indexer = EmbeddingIndexer(
        #     embedding_client=self.embedding,
        #     vector_store=vector_store,
        #     token_store=token_store,
        #     metadata_store=metadata_store,
        #     temporal_index=temporal_index,
        #     causal_graph=causal_graph,
        # )

        # -----------------------------------------
        # engine
        # -----------------------------------------

        engine = VectorIndex(
            components=components,
            embedding_service=self.embedding,
            tokenizer=self.tokenizer,
            memory_provider=self.memory_provider,
            entity_provider=self.entity_provider,
            context_provider=self.context_provider,
        )

        # -----------------------------------------
        # inicialização opcional
        # -----------------------------------------

        self._build_ann_index(components)
        self._build_clusters(components)

        return engine