import httpx
from rpg_narrative_server.infrastructure.llm.base_provider import BaseProvider


class OllamaProvider(BaseProvider):

    def __init__(self, model: str, base_url: str):
        super().__init__("ollama", model)
        self.client = httpx.AsyncClient(base_url=base_url)

    async def _call_api(self, request):
        return await self.client.post(
            "/api/generate",
            json={
                "model": self.model,
                "prompt": request.prompt,
                "stream": False,
            },
        )

    def _extract_content(self, resp):
        data = resp.json()
        return (data.get("response") or "").strip()
