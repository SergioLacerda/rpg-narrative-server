from rpg_narrative_server.vector_index.ranking.stage2_ranker import Stage2Ranker


class RankingStage2:
    def __init__(self):
        self.ranker = Stage2Ranker()

    async def run(self, ctx):
        candidates = ctx.candidates

        ranked = self.ranker.rank(ctx, candidates)

        ctx.stage2_candidates = ranked
        ctx.candidates = ranked

        return ctx
