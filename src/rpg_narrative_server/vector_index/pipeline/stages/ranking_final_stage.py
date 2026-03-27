from rpg_narrative_server.vector_index.ranking.ranking_final import RankingFinal

class RankingFinalStage:

    priority = 100

    def __init__(self):
        self.ranker = RankingFinal()

    async def run(self, ctx):

        if not ctx.candidates:
            ctx.results = []
            return ctx

        ctx.results = self.ranker.rank(ctx, ctx.candidates)

        return ctx