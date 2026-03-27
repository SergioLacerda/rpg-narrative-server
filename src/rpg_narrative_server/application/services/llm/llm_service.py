import json
import hashlib
import logging

from rpg_narrative_server.infrastructure.resilience.resilience import resilient_call

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
    # GENERATE
    # ---------------------------------------------------------

    async def generate(self, request):

        if not request.prompt:
            return ""

        key = self._cache_key(request)

        # L1 cache
        if self.ttl_cache:
            cached = self.ttl_cache.get(key)
            if cached:
                return cached

        # L2 cache
        if self.response_cache:
            cached = await self.response_cache.get(key)
            if cached:
                if self.ttl_cache:
                    self.ttl_cache.set(key, cached)
                return cached

        # ----------------------------------
        # 🔥 CIRCUIT BREAKER
        # ----------------------------------

        if self.circuit_breaker and not self.circuit_breaker.allow():
            logger.warning("Circuit breaker OPEN - skipping LLM call")
            raise RuntimeError("LLM circuit open")

        try:
            response = await resilient_call(
                self.provider.generate,
                request,
                timeout=self._compute_timeout(request),
            )

            if not response:
                return ""

            if self.circuit_breaker:
                self.circuit_breaker.success()

            if self.ttl_cache:
                self.ttl_cache.set(key, response)

            if self.response_cache:
                await self.response_cache.set(key, response)

            return response

        except Exception:
            if self.circuit_breaker:
                self.circuit_breaker.failure()

            logger.exception("LLM failure")
            raise

    # ---------------------------------------------------------
    # STREAM (🔥)
    # ---------------------------------------------------------

    async def stream(self, request):

        async for chunk in self.provider.stream(request):
            yield chunk

    # ---------------------------------------------------------

    def _cache_key(self, request):

        payload = {
            "prompt": request.prompt,
            "system": request.system_prompt,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    # ---------------------------------------------------------

    def _compute_timeout(self, request):

        if not request.max_tokens:
            return self.timeout

        dynamic = request.max_tokens * 0.2

        return max(30.0, min(dynamic, self.timeout))
