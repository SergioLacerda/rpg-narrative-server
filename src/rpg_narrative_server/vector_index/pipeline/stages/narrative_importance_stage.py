class NarrativeImportanceStage:
    priority = 105

    def __init__(self, importance_model=None):
        self.importance = importance_model

    async def run(self, ctx):
        if not ctx.candidates:
            ctx.results = []
            return ctx

        # fallback simples
        ctx.results = ctx.candidates[: getattr(ctx, "k", 4)]

        # se tiver modelo de importância
        if self.importance:
            try:
                ctx.results = self.importance.rank(ctx, ctx.candidates)
            except Exception:
                pass

        return ctx
