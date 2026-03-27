class RetrievalPipeline:

    def __init__(self, stages):
        self.stages = sorted(stages, key=lambda s: getattr(s, "priority", 50))

    def run(self, ctx):

        candidates = []

        for stage in self.stages:

            if candidates and len(candidates) < getattr(stage, "min_candidates", 0):
                continue

            candidates = stage.run(ctx, candidates)

        return candidates
