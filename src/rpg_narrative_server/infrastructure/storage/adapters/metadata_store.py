from rpg_narrative_server.vector_index.components import MetadataStore


class MetadataStoreAdapter(MetadataStore):

    def __init__(self, kv_store):
        self.store = kv_store

    def set(self, doc_id: str, metadata: dict):
        self.store.set(doc_id, metadata)

    def get(self, doc_id: str):
        return self.store.get(doc_id)