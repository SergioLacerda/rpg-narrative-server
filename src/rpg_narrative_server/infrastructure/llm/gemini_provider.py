try:
    import google.generativeai as genai
except ImportError:
    genai = None

from rpg_narrative_server.infrastructure.llm.base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        genai.configure(api_key=api_key)
        super().__init__("gemini", model)
        self.model_obj = genai.GenerativeModel(model)

    async def _call_api(self, request):
        return await self.model_obj.generate_content_async(request.prompt)

    def _extract_content(self, resp):
        return (getattr(resp, "text", "") or "").strip()
