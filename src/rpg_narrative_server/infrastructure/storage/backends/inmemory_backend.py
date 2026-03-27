from .base import StorageBackend

from rpg_narrative_server.infrastructure.storage.kv.in_memory_kv_store import (
    InMemoryKVStore,
)

from rpg_narrative_server.infrastructure.storage.adapters.document_store import (
    DocumentStoreAdapter,
)
from rpg_narrative_server.infrastructure.storage.adapters.token_store import (
    TokenStoreAdapter,
)
from rpg_narrative_server.infrastructure.storage.adapters.metadata_store import (
    MetadataStoreAdapter,
)
from rpg_narrative_server.infrastructure.storage.adapters.vector_store import (
    VectorStoreAdapter,
)


# ---------------------------------------------------------
# vector store simples
# ---------------------------------------------------------


class InMemoryVectorStore:
    def __init__(self):
        self.data = {}

    def add(self, doc_id, vector):
        self.data[doc_id] = vector

    def get(self, doc_id):
        return self.data.get(doc_id)

    def keys(self):
        return list(self.data.keys())

    def search(self, query_vector, k):
        return list(self.data.keys())[:k]

    def clear(self):
        self.data.clear()


# ---------------------------------------------------------
# backend
# ---------------------------------------------------------


class InMemoryStorageBackend(StorageBackend):
    def build_vector_store(self):
        return VectorStoreAdapter(InMemoryVectorStore())

    def build_document_store(self):
        return DocumentStoreAdapter(InMemoryKVStore())

    def build_token_store(self):
        return TokenStoreAdapter(InMemoryKVStore())

    def build_metadata_store(self):
        return MetadataStoreAdapter(InMemoryKVStore())
