import logging
import time
from abc import ABC, abstractmethod

from rpg_narrative_server.application.dto.llm_request import LLMRequest
from rpg_narrative_server.application.dto.llm_response import LLMResponse
from rpg_narrative_server.application.services.llm.error_mapper import map_http_error
from rpg_narrative_server.application.services.llm.llm_errors import (
    LLMClientError,
    LLMRetryableError,
)


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
    # ENTRYPOINT
    # ---------------------------------------------------------

    async def generate(self, request: LLMRequest) -> LLMResponse:
        self.logger.warning("🔥 USING PROVIDER: %s", self.provider_name)
        return await self.generate_from_request(request)

    # ---------------------------------------------------------

    async def generate_from_request(self, request: LLMRequest) -> LLMResponse:
        start = time.perf_counter()

        try:
            self.logger.debug("BEGIN model=%s", self.model)

            resp = await self._call_api(request)

            # -------------------------------------------------
            # EXTRAÇÃO + NORMALIZAÇÃO
            # -------------------------------------------------
            content = self._extract_content(resp)

            if content is None:
                content = ""

            if not isinstance(content, str):
                content = str(content)

            # -------------------------------------------------
            # VALIDAÇÃO ROBUSTA
            # -------------------------------------------------
            if not content.strip():
                self._log_empty_response(resp)
                raise LLMRetryableError("Empty response")

            # -------------------------------------------------
            # MÉTRICAS
            # -------------------------------------------------
            latency = (time.perf_counter() - start) * 1000

            self.logger.debug("SUCCESS latency=%.2fms", latency)

            usage = self._extract_usage(resp) or {}

            # -------------------------------------------------
            # RESPONSE PADRONIZADO
            # -------------------------------------------------
            return LLMResponse(
                content=content,
                provider=self.provider_name,
                model=self.model,
                latency_ms=latency,
                **usage,
            )

        # ---------------------------------------------------------
        # ERROS
        # ---------------------------------------------------------

        except TimeoutError as e:
            raise ValueError("timeout") from e

        except ValueError as e:
            raise LLMClientError(str(e)) from e

        except LLMRetryableError:
            raise

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

    # ---------------------------------------------------------
    # OPCIONAIS
    # ---------------------------------------------------------

    def _extract_usage(self, resp) -> dict:
        return {}

    # ---------------------------------------------------------
    # DEBUG / OBSERVABILIDADE
    # ---------------------------------------------------------

    def _log_empty_response(self, resp):
        try:
            import json

            if hasattr(resp, "model_dump"):
                raw = resp.model_dump()
                self.logger.error("EMPTY CONTENT | raw=%s", json.dumps(raw))
            else:
                self.logger.error("EMPTY CONTENT | raw=%s", repr(resp))

        except Exception:
            self.logger.error("EMPTY CONTENT | failed to serialize response")
