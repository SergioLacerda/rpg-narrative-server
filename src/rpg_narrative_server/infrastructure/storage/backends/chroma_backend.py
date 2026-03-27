from pathlib import Path

from rpg_narrative_server.infrastructure.storage.backends.base import StorageBackend

from rpg_narrative_server.infrastructure.storage.adapters.vector_store import (
    VectorStoreAdapter,
)
from rpg_narrative_server.infrastructure.storage.kv.in_memory_kv_store import (
    InMemoryKVStore,
)


class ChromaStorageBackend(StorageBackend):
    def __init__(self, base_path: Path | None = None):
        self.base = base_path or Path("./data")
        self.base.mkdir(parents=True, exist_ok=True)

        self.client = self._load_chroma_lib()

    def _load_chroma_lib(self):
        try:
            import chromadb

            return chromadb.Client(
                chromadb.config.Settings(
                    persist_directory=str(self.base / "chroma"),
                    anonymized_telemetry=False,
                )
            )
        except ImportError as e:
            raise RuntimeError(
                "ChromaStorageBackend requires optional dependency 'chromadb'. "
                "Install with: pip install rpg_narrative_server[vector-db]"
            ) from e

    def _get_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

    # ---------------------------------------------------------
    # STORES
    # ---------------------------------------------------------

    def build_vector_store(self):
        from rpg_narrative_server.infrastructure.storage.vector.chroma_vector_store import (
            ChromaVectorStore,
        )

        collection = self._get_collection("vectors")
        return VectorStoreAdapter(ChromaVectorStore(collection))

    def build_document_store(self):
        return InMemoryKVStore()

    def build_token_store(self):
        return InMemoryKVStore()

    def build_metadata_store(self):
        return InMemoryKVStore()
