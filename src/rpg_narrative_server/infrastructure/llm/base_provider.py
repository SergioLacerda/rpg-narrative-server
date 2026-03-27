import logging
import time
from abc import ABC, abstractmethod

from rpg_narrative_server.application.dto.llm_request import LLMRequest
from rpg_narrative_server.application.dto.llm_response import LLMResponse
from rpg_narrative_server.application.services.llm.llm_errors import (
    LLMRetryableError,
    LLMClientError,
)
from rpg_narrative_server.application.services.llm.error_mapper import map_http_error


class BaseProvider(ABC):
    """
    Base para todos providers LLM.

    Responsável por:
    - timeout
    - logging
    - error handling
    - validação de resposta
    """

    def __init__(self, provider_name: str, model: str, timeout: float | None = None):
        self.provider_name = provider_name
        self.model = model
        self.timeout = timeout
        self.logger = logging.getLogger(f"rpg_narrative_server.llm.{provider_name}")

    # ---------------------------------------------------------

    async def generate(self, request: LLMRequest) -> str:
        response = await self.generate_from_request(request)
        return response.content

    # ---------------------------------------------------------

    async def generate_from_request(self, request: LLMRequest) -> LLMResponse:

        start = time.perf_counter()

        try:
            self.logger.debug("BEGIN model=%s", self.model)

            resp = await self._call_api(request)

            content = self._extract_content(resp)

            if not content:
                raise LLMRetryableError("Empty response")

            latency = (time.perf_counter() - start) * 1000

            self.logger.debug("SUCCESS latency=%.2fms", latency)

            return LLMResponse(
                content=content,
                provider=self.provider_name,
                model=self.model,
                latency_ms=latency,
                **self._extract_usage(resp),
            )

        except ValueError as e:
            raise LLMClientError(str(e)) from e

        except Exception as e:

            status = getattr(e, "status_code", None)
            if status:
                map_http_error(status, str(e))

            self.logger.exception("FAIL model=%s", self.model)

            raise LLMRetryableError(str(e)) from e

    # ---------------------------------------------------------
    # EXTENSÃO (cada provider implementa)
    # ---------------------------------------------------------

    @abstractmethod
    async def _call_api(self, request: LLMRequest):
        pass

    @abstractmethod
    def _extract_content(self, resp) -> str:
        pass

    # opcional
    def _extract_usage(self, resp) -> dict:
        return {}