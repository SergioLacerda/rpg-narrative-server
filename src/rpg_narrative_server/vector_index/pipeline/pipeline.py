import inspect


class RetrievalPipeline:
    def __init__(self, stages):
        self.stages = sorted(stages, key=lambda s: getattr(s, "priority", 50))

    async def run(self, ctx):
        for stage in self.stages:
            if ctx.candidates is not None and len(ctx.candidates) < getattr(
                stage, "min_candidates", 0
            ):
                continue

            result = stage.run(ctx)

            if inspect.isawaitable(result):
                ctx = await result
            else:
                ctx = result

        return ctx
