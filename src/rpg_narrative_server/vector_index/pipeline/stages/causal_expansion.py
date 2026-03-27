class CausalExpansion:

    priority = 17

    def __init__(self, causal_graph=None):
        self.graph = causal_graph

    async def run(self, ctx):

        if not self.graph or not ctx.candidates:
            return ctx

        expanded = set(ctx.candidates)

        extra = self.graph.expand(ctx.candidates, depth=2)

        expanded.update(extra)

        ctx.candidates = list(expanded)

        return ctx