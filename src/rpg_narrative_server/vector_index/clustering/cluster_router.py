class ClusterRouter:
    """
    Seleciona clusters relevantes para query.
    """

    def __init__(self, cluster_manager):
        self.manager = cluster_manager

    def route(self, candidates):

        # estratégia simples:
        # retorna 1 item por cluster

        seen = set()
        result = []

        for doc_id in candidates:

            cluster = self.manager.get_cluster(doc_id)
            cluster_id = tuple(sorted(cluster))

            if cluster_id in seen:
                continue

            seen.add(cluster_id)
            result.append(doc_id)

        return result