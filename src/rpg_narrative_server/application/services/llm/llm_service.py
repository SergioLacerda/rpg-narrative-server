import json
import logging

from rpg_narrative_server.shared.hash_utils import sha256_hash
from rpg_narrative_server.shared.resilience import resilient_call

logger = logging.getLogger("rpg_narrative_server.llm")


class LLMService:
    def __init__(
        self,
        provider,
        *,
        response_cache=None,
        ttl_cache=None,
        timeout: float = 60.0,
        circuit_breaker=None,
    ):
        self.provider = provider
        self.response_cache = response_cache
        self.ttl_cache = ttl_cache
        self.timeout = timeout
        self.circuit_breaker = circuit_breaker

    # ---------------------------------------------------------
    # CACHE KEY (FINAL)
    # ---------------------------------------------------------

    def _cache_key(self, request):
        campaign_id = getattr(request, "campaign_id", None)

        payload = {
            "campaign_id": campaign_id,
            "prompt": request.prompt or "",
            "system": request.system_prompt or "",
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        if hasattr(request, "metadata") and request.metadata:
            payload["metadata"] = request.metadata

        if hasattr(request, "tools") and request.tools:
            payload["tools"] = request.tools

        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)

        return sha256_hash(raw.encode("utf-8"))

    # ---------------------------------------------------------
    # GENERATE
    # ---------------------------------------------------------

    async def generate(self, request):
        if not request.prompt:
            print("Erroe: 1")
            return ""

        key = self._cache_key(request)

        # L1
        if self.ttl_cache:
            cached = self.ttl_cache.get(key)
            if cached:
                print("Erroe: 2")
                return cached

        # L2
        if self.response_cache:
            cached = await self.response_cache.get(key)

            print("CACHE TYPE:", type(self.response_cache))
            print("CACHE DIR:", dir(self.response_cache))

            if cached:
                if self.ttl_cache:
                    self.ttl_cache.set(key, cached)
                print("Erroe: 3")
                return cached

        # Circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.allow():
            raise RuntimeError("LLM circuit open")

        try:
            response = await resilient_call(
                self.provider.generate,
                request,
                timeout=self._compute_timeout(request),
            )

            if response is None:
                print("Erroe: 4")
                return None

            if self.circuit_breaker:
                self.circuit_breaker.success()

            if self.ttl_cache:
                self.ttl_cache.set(key, response)

            if self.response_cache:
                await self.response_cache.set(key, response)

            print("Return ")
            return response

        except Exception:
            if self.circuit_breaker:
                self.circuit_breaker.failure()

            logger.exception("LLM failure")
            raise

    # ---------------------------------------------------------

    async def stream(self, request):
        async for chunk in self.provider.stream(request):
            yield chunk

    # ---------------------------------------------------------

    def _compute_timeout(self, request):
        if not request.max_tokens:
            return self.timeout

        dynamic = request.max_tokens * 0.2
        return max(30.0, min(dynamic, self.timeout))
