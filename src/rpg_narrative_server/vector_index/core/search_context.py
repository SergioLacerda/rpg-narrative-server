class SearchContext:

    def __init__(
        self,
        query,
        q_vec,
        query_tokens,
        query_type,
        vector_store,
        k: int = 4,
        token_store=None,
        metadata_store=None,
        ann=None,
        temporal_index=None,
    ):
        self.query = query
        self.q_vec = q_vec
        self.query_tokens = query_tokens
        self.query_type = query_type

        self.vector_store = vector_store
        self.token_store = token_store
        self.metadata_store = metadata_store

        self.k = k

        self.ann = ann
        self.temporal_index = temporal_index

        # 🔥 pipeline state
        self.candidates = []
        self.results = []

        # caches
        self._token_cache = {}
        self._meta_cache = {}

    # -----------------------------------------
    # helpers
    # -----------------------------------------

    def get_vector(self, doc_id):
        return self.vector_store.get(doc_id)

    def get_tokens(self, doc_id):

        if doc_id in self._token_cache:
            return self._token_cache[doc_id]

        tokens = self.token_store.get(doc_id) if self.token_store else None
        self._token_cache[doc_id] = tokens
        return tokens

    def get_metadata(self, doc_id):

        if doc_id in self._meta_cache:
            return self._meta_cache[doc_id]

        meta = self.metadata_store.get(doc_id) if self.metadata_store else None
        self._meta_cache[doc_id] = meta
        return meta
