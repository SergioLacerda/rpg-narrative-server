class QueryLocalCache:

    priority = 30

    def __init__(self):
        self.cache = {}

    async def run(self, ctx):

        key = ctx.query

        if key in self.cache:
            ctx.candidates = self.cache[key]
            ctx._cache_hit = True
            return ctx

        ctx._cache_hit = False
        return ctx

    def save(self, query, candidates):
        self.cache[query] = candidates