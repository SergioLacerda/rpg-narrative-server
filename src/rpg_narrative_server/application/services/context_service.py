class ContextService:

    def __init__(self, retrieval_service):
        self.retrieval = retrieval_service

    async def search(self, query: str, k: int = 4):

        docs = await self.retrieval.search(query, k=k)

        return [d["text"] for d in docs if d]
