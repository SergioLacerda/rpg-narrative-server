class FakeEmbeddingService:
    async def embed(self, text: str):
        return [0.1, 0.2, 0.3]


class FakeDocumentStore:

    def __init__(self):
        self.store = {}

    async def add(self, doc_id=None, content=None, **kwargs):
        if doc_id:
            self.store[doc_id] = {"content": content or "fake content"}

    def get(self, doc_id):

        if isinstance(doc_id, dict):
            return doc_id

        return self.store.get(doc_id, {"content": "fake resolved doc"})


class FakeMetadataStore:

    def __init__(self):
        self.store = {}

    async def add(self, doc_id=None, metadata=None, **kwargs):
        if doc_id:
            self.store[doc_id] = metadata or {}

    def get(self, doc_id):

        if isinstance(doc_id, dict):
            return {}

        return self.store.get(doc_id, {})


class FakeComponents:
    def __init__(self):
        self.document_store = FakeDocumentStore()
        self.metadata_store = FakeMetadataStore()


class FakeVectorIndex:

    def __init__(self):
        self.docs = []
        self.embedding_service = FakeEmbeddingService()
        self.components = FakeComponents()

    @property
    def vector_store(self):
        return self.docs

    async def search(self, query, k=4):
        return self.docs[:k] or ["fake context"]

    async def search_async(self, query: str, k: int = 5):
        return [{"content": f"doc about {query}", "score": 0.9}]

    async def index_campaign(self, *args, **kwargs):
        self.docs.append("fake context")
        return self.docs
