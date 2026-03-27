import random


class CandidateSetReservoir:

    priority = 50

    def __init__(self, max_size=100):
        self.max_size = max_size

    async def run(self, ctx):

        if not ctx.candidates:
            return ctx

        if len(ctx.candidates) > self.max_size:
            ctx.candidates = random.sample(ctx.candidates, self.max_size)

        return ctx