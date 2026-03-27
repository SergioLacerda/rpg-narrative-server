class RetrievalService:
    def __init__(self, vector_index, planner, context_window, selector):
        self.vector_index = vector_index
        self.planner = planner
        self.context_window = context_window
        self.selector = selector

    async def search(self, query, k=4):
        docs = await self.vector_index.search(query, k=k)

        docs = self.selector.select(docs)

        policy = self.context_window.get_policy(query)
        docs = self.context_window.apply(docs, policy)

        return docs
