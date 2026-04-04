try:
    import anthropic
except ImportError:
    anthropic = None

from rpg_narrative_server.infrastructure.adapters.llm.base_provider import BaseProvider


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        super().__init__("anthropic", model)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def _call_api(self, request):
        return await self.client.messages.create(
            model=self.model,
            max_tokens=request.max_tokens,
            messages=[{"role": "user", "content": request.prompt}],
        )

    def _extract_content(self, resp):
        parts = []
        for block in getattr(resp, "content", []):
            if getattr(block, "text", None):
                parts.append(block.text)
        return "".join(parts).strip()
