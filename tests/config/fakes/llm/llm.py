class DummyLLM:

    def __init__(self, result="ACTION"):
        self.result = result
        self.calls = []

    async def generate(self, request):
        self.calls.append({
            "prompt": request.prompt,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        })
        return self.result