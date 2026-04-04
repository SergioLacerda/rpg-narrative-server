from pathlib import Path

from rpg_narrative_server.infrastructure.adapters.storage.adapters.document_store import (
    DocumentStoreAdapter,
)
from rpg_narrative_server.infrastructure.adapters.storage.adapters.metadata_store import (
    MetadataStoreAdapter,
)
from rpg_narrative_server.infrastructure.adapters.storage.adapters.token_store import (
    TokenStoreAdapter,
)
from rpg_narrative_server.infrastructure.adapters.storage.adapters.vector_store import (
    VectorStoreAdapter,
)
from rpg_narrative_server.infrastructure.adapters.storage.backends.base import StorageBackend
from rpg_narrative_server.infrastructure.adapters.storage.bootstrap import (
    ensure_memory_structure,
    ensure_storage_structure,
)
from rpg_narrative_server.infrastructure.adapters.storage.kv.json_kv_store import (
    JSONKeyValueStore,
)
from rpg_narrative_server.infrastructure.adapters.storage.vector.json_vector_store import (
    JSONVectorStore,
)
from rpg_narrative_server.infrastructure.adapters.storage.vector_store_config import (
    VectorStoreConfig,
)


class JSONStorageBackend(StorageBackend):
    """
    Backend baseado em arquivos JSON.

    ✔ Persistente
    ✔ Simples
    ✔ Ideal para dev / protótipo / low-scale
    """

    def __init__(self, base_path: Path, config: VectorStoreConfig = None):
        self.base = base_path
        self._ensure_base()
        self.config = config or VectorStoreConfig()

    # ---------------------------------------------------------
    # setup
    # ---------------------------------------------------------

    def _ensure_base(self):
        ensure_storage_structure(self.base)
        ensure_memory_structure(self.base)

    def _kv(self, name: str) -> JSONKeyValueStore:
        return JSONKeyValueStore(self.base / f"{name}.json")

    # ---------------------------------------------------------
    # factories
    # ---------------------------------------------------------

    def build_vector_store(self):
        return VectorStoreAdapter(JSONVectorStore(self.base / "vectors.json", self.config))

    def build_document_store(self):
        return DocumentStoreAdapter(self._kv("documents"))

    def build_token_store(self):
        return TokenStoreAdapter(self._kv("tokens"))

    def build_metadata_store(self):
        return MetadataStoreAdapter(self._kv("metadata"))
