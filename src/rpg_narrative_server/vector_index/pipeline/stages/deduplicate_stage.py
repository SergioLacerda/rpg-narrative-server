class DeduplicateStage:

    priority = 75

    async def run(self, ctx):

        if not ctx.candidates:
            return ctx

        seen = set()
        unique = []

        for doc_id in ctx.candidates:
            if doc_id not in seen:
                seen.add(doc_id)
                unique.append(doc_id)

        ctx.candidates = unique

        return ctx
