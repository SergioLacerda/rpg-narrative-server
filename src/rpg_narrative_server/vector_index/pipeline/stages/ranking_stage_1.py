class RankingStage1:

    def __init__(self, ranker):
        self.ranker = ranker

    async def run(self, ctx):
        candidates = ctx.candidates

        ranked = self.ranker.rank(ctx, candidates)

        ctx.stage1_candidates = ranked
        ctx.candidates = ranked

        return ctx
