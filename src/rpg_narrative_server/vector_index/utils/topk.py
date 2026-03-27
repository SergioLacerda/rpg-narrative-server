import heapq
from typing import Any, List, Tuple


class TopK:
    """
    Mantém os top-k elementos baseado em score.
    """

    def __init__(self, k: int):
        if k <= 0:
            raise ValueError("k must be > 0")

        self.k = k
        self._heap: List[Tuple[float, Any]] = []

    # ---------------------------------------------------------
    # inserir item
    # ---------------------------------------------------------

    def push(self, score: float, item: Any):

        if len(self._heap) < self.k:
            heapq.heappush(self._heap, (score, item))
        else:
            heapq.heappushpop(self._heap, (score, item))

    # ---------------------------------------------------------
    # retornar resultados ordenados
    # ---------------------------------------------------------

    def results(self) -> List[Any]:

        return [item for _, item in sorted(self._heap, reverse=True)]

    # ---------------------------------------------------------
    # retornar com score (debug útil)
    # ---------------------------------------------------------

    def results_with_scores(self) -> List[Tuple[float, Any]]:

        return sorted(self._heap, reverse=True)

    # ---------------------------------------------------------
    # limpar
    # ---------------------------------------------------------

    def clear(self):
        self._heap.clear()

    # ---------------------------------------------------------
    # tamanho atual
    # ---------------------------------------------------------

    def __len__(self):
        return len(self._heap)
