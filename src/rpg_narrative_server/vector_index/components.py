from dataclasses import dataclass
from typing import Protocol, runtime_checkable, Iterable, Any, Optional


# ==========================================================
# PROTOCOLS (CONTRATOS)
# ==========================================================

@runtime_checkable
class VectorStore(Protocol):
    def add(self, doc_id: str, vector: list[float]) -> None: ...
    def get(self, doc_id: str) -> list[float] | None: ...
    def search(self, query_vector: list[float], k: int) -> list[str]: ...
    def keys(self) -> list[str]: ...


@runtime_checkable
class DocumentStore(Protocol):
    def set(self, doc_id: str, document: dict) -> None: ...
    def get(self, doc_id: str) -> dict | None: ...


@runtime_checkable
class TokenStore(Protocol):
    def set(self, doc_id: str, tokens: Any) -> None: ...
    def get(self, doc_id: str) -> Any: ...


@runtime_checkable
class MetadataStore(Protocol):
    def set(self, doc_id: str, metadata: dict) -> None: ...
    def get(self, doc_id: str) -> dict | None: ...


@runtime_checkable
class Ranker(Protocol):
    def rank(self, ctx, candidates) -> list[str]: ...


@runtime_checkable
class QueryClassifier(Protocol):
    def classify(self, query: str) -> str: ...


@runtime_checkable
class IVFBuilder(Protocol):
    def build(self, doc_ids: list[str], vector_store: VectorStore): ...


@runtime_checkable
class IVFRouter(Protocol):
    def set_index(self, index) -> None: ...
    def route(self, query_vector: list[float]) -> Iterable[int]: ...
    def search(self, query_vector: list[float]) -> list[str]: ...


@runtime_checkable
class ClusterManager(Protocol):
    def update(self, doc_ids: list[str], vector_store: VectorStore): ...


# 🔥 NOVO — evita Any
@runtime_checkable
class ClusterRouter(Protocol):
    def route(self, query_vector: list[float]) -> list[str]: ...


# ==========================================================
# COMPONENT CONTAINER
# ==========================================================

@dataclass(slots=True)
class VectorIndexComponents:
    """
    Boundary do sub-sistema de busca vetorial.

    ✔ Apenas contratos
    ✔ Sem lógica
    ✔ Sem dependência de infra externa
    """

    # ---------------------------------------------------------
    # classificação / controle
    # ---------------------------------------------------------

    query_classifier: QueryClassifier

    # ---------------------------------------------------------
    # ranking
    # ---------------------------------------------------------

    stage1_ranker: Ranker
    stage2_ranker: Ranker

    # ---------------------------------------------------------
    # clustering
    # ---------------------------------------------------------

    cluster_manager: ClusterManager

    # ---------------------------------------------------------
    # stores
    # ---------------------------------------------------------

    vector_store: VectorStore
    document_store: DocumentStore
    token_store: TokenStore
    metadata_store: MetadataStore

    # ---------------------------------------------------------
    # ANN
    # ---------------------------------------------------------

    ivf_builder: IVFBuilder
    ivf_router: IVFRouter

    # ---------------------------------------------------------
    # narrativa (opcional)
    # ---------------------------------------------------------

    temporal_index: Optional[Any] = None
    causal_graph: Optional[Any] = None

    # ---------------------------------------------------------
    # config
    # ---------------------------------------------------------

    vector_dim: int = 768

    # ---------------------------------------------------------
    # opcionais (🔥 SEMPRE NO FINAL)
    # ---------------------------------------------------------

    cluster_router: Optional[ClusterRouter] = None

    # ==========================================================
    # VALIDATION
    # ==========================================================

    # ==========================================================
    # ANN (ABSTRAÇÃO)
    # ==========================================================

    @runtime_checkable
    class ANN(Protocol):
        """
        Contrato unificado para mecanismos de busca vetorial.

        🔥 REGRAS:
        - search é OBRIGATÓRIO
        - NÃO expõe detalhes internos (clusters, graph, etc)
        """

    def search(self, query_vector: list[float], k: int = 10) -> list[str]: ...

    def validate(self) -> None:
        """
        Garante integridade estrutural dos componentes.
        """

        # stores
        assert isinstance(self.vector_store, VectorStore), "Invalid vector_store"
        assert isinstance(self.document_store, DocumentStore), "Invalid document_store"
        assert isinstance(self.token_store, TokenStore), "Invalid token_store"
        assert isinstance(self.metadata_store, MetadataStore), "Invalid metadata_store"

        # ranking
        assert isinstance(self.stage1_ranker, Ranker), "Invalid stage1_ranker"
        assert isinstance(self.stage2_ranker, Ranker), "Invalid stage2_ranker"

        # classifier
        assert isinstance(self.query_classifier, QueryClassifier), "Invalid query_classifier"

        # ANN
        assert isinstance(self.ivf_builder, IVFBuilder), "Invalid ivf_builder"
        assert isinstance(self.ivf_router, IVFRouter), "Invalid ivf_router"

        # clustering
        assert isinstance(self.cluster_manager, ClusterManager), "Invalid cluster_manager"

        # opcional
        if self.cluster_router is not None:
            assert isinstance(self.cluster_router, ClusterRouter), "Invalid cluster_router"