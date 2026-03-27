from collections import defaultdict


class CausalityGraph:
    """
    Grafo causal simples entre documentos.

    doc A → doc B (A influencia B)
    """

    def __init__(self):
        self.forward = defaultdict(list)   # A -> [B, C]
        self.backward = defaultdict(list)  # B -> [A]

    # ---------------------------------------------------------
    # adicionar relação
    # ---------------------------------------------------------

    def add_edge(self, source: str, target: str):

        self.forward[source].append(target)
        self.backward[target].append(source)

    # ---------------------------------------------------------
    # expansão causal
    # ---------------------------------------------------------

    def expand(self, doc_ids, depth=2):

        visited = set(doc_ids)
        frontier = set(doc_ids)

        for _ in range(depth):

            new_nodes = set()

            for doc_id in frontier:

                # forward
                for nxt in self.forward.get(doc_id, []):
                    if nxt not in visited:
                        new_nodes.add(nxt)

                # backward
                for prev in self.backward.get(doc_id, []):
                    if prev not in visited:
                        new_nodes.add(prev)

            visited.update(new_nodes)
            frontier = new_nodes

        return list(visited)