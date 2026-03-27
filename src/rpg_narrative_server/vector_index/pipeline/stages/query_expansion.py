import tokenize
from collections import Counter


class QueryExpansion:

    priority = 10

    def __init__(
        self,
        memory_provider,
        max_terms: int = 5,
        min_token_length: int = 3,
    ):
        self.memory = memory_provider
        self.max_terms = max_terms
        self.min_token_length = min_token_length

    async def run(self, ctx):

        query = ctx.query

        if not query or not self.memory:
            return ctx

        # -----------------------------------------
        # contexto recente
        # -----------------------------------------

        try:
            events = self.memory.get_recent()
        except Exception:
            return ctx

        if not events:
            return ctx

        # -----------------------------------------
        # tokens
        # -----------------------------------------

        tokens = []
        for e in events:
            tokens.extend(tokenize(e))

        if not tokens:
            return ctx

        # -----------------------------------------
        # frequência
        # -----------------------------------------

        freq = Counter(tokens)

        candidates = [
            t for t, _ in freq.most_common() if len(t) >= self.min_token_length
        ]

        if not candidates:
            return ctx

        # -----------------------------------------
        # expansão
        # -----------------------------------------

        query_tokens = set(ctx.query_tokens or [])

        extra_terms = [t for t in candidates[: self.max_terms] if t not in query_tokens]

        if not extra_terms:
            return ctx

        expanded_query = query + " " + " ".join(extra_terms)

        ctx.query = expanded_query
        ctx.query_tokens = tokenize(expanded_query)
        ctx.expanded_terms = extra_terms

        return ctx
