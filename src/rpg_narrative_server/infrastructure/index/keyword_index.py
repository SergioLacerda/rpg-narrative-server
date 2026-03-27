import re
from collections import defaultdict, Counter
from typing import List, Tuple


class KeywordIndex:
    """
    Índice invertido simples para busca por palavras-chave.
    Usado como fallback leve para queries curtas.
    """

    def __init__(self):

        self.index = defaultdict(set)

    # ---------------------------------------------------------
    # tokenização
    # ---------------------------------------------------------

    def _tokens(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    # ---------------------------------------------------------
    # indexação
    # ---------------------------------------------------------

    def add(self, text: str, key: str):

        for token in self._tokens(text):
            self.index[token].add(key)

    # ---------------------------------------------------------
    # busca
    # ---------------------------------------------------------

    def search(
        self,
        text: str,
        limit: int = 5,
        min_score: int = 1,
    ) -> List[Tuple[str, int]]:

        tokens = self._tokens(text)

        scores = Counter()

        for token in tokens:

            for key in self.index.get(token, []):
                scores[key] += 1

        if not scores:
            return []

        results = [
            (key, score)
            for key, score in scores.items()
            if score >= min_score
        ]

        # ordena por score
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    # ---------------------------------------------------------
    # compatibilidade (legado)
    # ---------------------------------------------------------

    def lookup(self, text: str) -> str | None:
        """
        Mantido para compatibilidade com código antigo.
        """

        results = self.search(text, limit=1, min_score=2)

        if not results:
            return None

        return results[0][0]