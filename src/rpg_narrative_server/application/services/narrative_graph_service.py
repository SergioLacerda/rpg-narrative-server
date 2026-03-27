class NarrativeGraphService:
    """
    Orquestra graph + extractor + repository.
    """

    def __init__(self, repo, extractor):

        self.repo = repo
        self.extractor = extractor

    # ---------------------------------------------------------
    # update
    # ---------------------------------------------------------

    def update_from_text(self, text: str):

        graph = self.repo.load()

        entities = self.extractor.extract(text)

        if not entities:
            return

        graph.update(entities)

        self.repo.save(graph)

    # ---------------------------------------------------------
    # query
    # ---------------------------------------------------------

    def related(self, query: str) -> set[str]:

        graph = self.repo.load()

        entities = self.extractor.extract(query)

        if not entities:
            return set()

        return graph.related(entities)
