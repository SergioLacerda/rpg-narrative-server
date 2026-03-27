from rpg_narrative_server.vector_index.components import TokenStore


class TokenStoreAdapter(TokenStore):

    def __init__(self, kv_store):
        self.store = kv_store

    def set(self, doc_id: str, tokens):
        self.store.set(doc_id, tokens)

    def get(self, doc_id: str):
        return self.store.get(doc_id)