from openai import AsyncOpenAI

from rpg_narrative_server.infrastructure.adapters.llm.base_provider import BaseProvider


class GroqProvider(BaseProvider):
    def __init__(self, api_key: str, model: str):
        super().__init__("groq", model)

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    async def _call_api(self, request):
        return await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": request.prompt}],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    def _extract_content(self, resp):
        if not resp.choices:
            return ""
        return (resp.choices[0].message.content or "").strip()

    def _extract_usage(self, resp):
        return {
            "tokens_input": getattr(resp.usage, "prompt_tokens", None),
            "tokens_output": getattr(resp.usage, "completion_tokens", None),
        }
