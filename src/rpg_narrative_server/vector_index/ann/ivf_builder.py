import random

from rpg_narrative_server.vector_index.ann.ivf_index import IVFIndex
from rpg_narrative_server.vector_index.utils.similarity import cosine_similarity


class IVFBuilder:

    def __init__(self, n_clusters=128, iterations=8):
        self.n_clusters = n_clusters
        self.iterations = iterations

    def build(self, doc_ids, vector_store):

        vectors = []
        valid_ids = []

        for doc_id in doc_ids:
            vec = vector_store.get(doc_id)
            if vec:
                vectors.append(vec)
                valid_ids.append(doc_id)

        if len(vectors) < 10:
            return None

        k = min(self.n_clusters, int(len(vectors) ** 0.5))

        centroids = random.sample(vectors, k)

        for _ in range(self.iterations):

            clusters = [[] for _ in centroids]

            for v in vectors:

                best = max(
                    range(len(centroids)),
                    key=lambda i: cosine_similarity(v, centroids[i])
                )

                clusters[best].append(v)

            new_centroids = []

            for cluster in clusters:
                if not cluster:
                    new_centroids.append(random.choice(vectors))
                    continue

                dim = len(cluster[0])
                mean = [0.0] * dim

                for v in cluster:
                    for i in range(dim):
                        mean[i] += v[i]

                mean = [x / len(cluster) for x in mean]
                new_centroids.append(mean)

            centroids = new_centroids

        inverted = {i: [] for i in range(len(centroids))}
        doc_map = {}

        for doc_id, vec in zip(valid_ids, vectors):

            best = max(
                range(len(centroids)),
                key=lambda i: cosine_similarity(vec, centroids[i])
            )

            inverted[best].append(doc_id)
            doc_map[doc_id] = best

        return IVFIndex(centroids, inverted, doc_map, vector_store=vector_store,)