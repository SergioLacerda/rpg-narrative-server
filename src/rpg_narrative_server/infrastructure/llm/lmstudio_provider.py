import httpx
from openai import AsyncOpenAI

from rpg_narrative_server.infrastructure.llm.base_provider import BaseProvider


class LMStudioProvider(BaseProvider):
    def __init__(self, base_url: str, model: str, timeout: float = 60.0):
        if not base_url.endswith("/v1"):
            base_url = base_url.rstrip("/") + "/v1"

        super().__init__("lmstudio", model)

        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="lm-studio",
            timeout=httpx.Timeout(timeout),
        )

    # ---------------------------------------------------------
    # CALL PADRÃO
    # ---------------------------------------------------------

    async def _call_api(self, request):
        messages = self._build_messages(request)

        try:
            return await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=min(request.max_tokens, 400),
            )

        except TimeoutError as e:
            raise TimeoutError("LM Studio timeout.") from e

        except ValueError as e:
            raise ValueError("LM Studio error.") from e

        except Exception as e:
            raise Exception("LM Studio exception.") from e

    # ---------------------------------------------------------

    def _extract_content(self, resp):
        if not resp or not resp.choices:
            return ""

        return (resp.choices[0].message.content or "").strip()

    # ---------------------------------------------------------
    # STREAMING (🔥)
    # ---------------------------------------------------------

    async def stream(self, request):
        messages = self._build_messages(request)

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=min(request.max_tokens, 400),
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    # ---------------------------------------------------------

    def _build_messages(self, request):
        messages = []

        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        messages.append({"role": "user", "content": request.prompt})

        return messages
