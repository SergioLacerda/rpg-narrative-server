from collections import defaultdict


class NarrativeGraph:
    """
    Representa relações entre entidades da narrativa.
    Não conhece IO, nem NLP.
    """

    def __init__(self):

        self._graph = defaultdict(set)

    # ---------------------------------------------------------
    # atualização
    # ---------------------------------------------------------

    def update(self, entities: list[str]):

        for e in entities:

            for other in entities:

                if e == other:
                    continue

                self._graph[e].add(other)

    # ---------------------------------------------------------
    # consulta
    # ---------------------------------------------------------

    def related(self, entities: list[str]) -> set[str]:

        result = set()

        for e in entities:
            result.update(self._graph.get(e, set()))

        return result

    # ---------------------------------------------------------
    # serialização
    # ---------------------------------------------------------

    def to_dict(self) -> dict:

        return {k: list(v) for k, v in self._graph.items()}

    @classmethod
    def from_dict(cls, data: dict):

        instance = cls()

        for k, values in data.items():
            instance._graph[k] = set(values)

        return instance
