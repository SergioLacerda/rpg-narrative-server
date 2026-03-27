class ClusterManager:
    """
    Mantém clusters atualizados.
    """

    def __init__(self, builder):
        self.builder = builder
        self.clusters = []

    def update(self, doc_ids, vector_store):

        self.clusters = self.builder.build(doc_ids, vector_store)

    def get_cluster(self, doc_id):

        for cluster in self.clusters:
            if doc_id in cluster:
                return cluster

        return [doc_id]