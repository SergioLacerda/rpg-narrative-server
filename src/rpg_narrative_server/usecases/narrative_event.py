import asyncio
from asyncio import Task, CancelledError, TimeoutError
import logging
from typing import Any, Tuple, Optional

from rpg_narrative_server.application.dto.llm_request import LLMRequest

from rpg_narrative_server.application.services.context_selector import ContextSelector
from rpg_narrative_server.application.services.intent.intent_classifier import (
    IntentClassifier,
)
from rpg_narrative_server.application.services.intent.llm_intent_classifier import (
    LLMIntentClassifier,
)
from rpg_narrative_server.application.services.intent.language_profiles import (
    SUPPORTED_LANGUAGES,
)

from rpg_narrative_server.domain.rag.retrieval_selector import RetrievalSelector
from rpg_narrative_server.domain.rag.context_window import DynamicContextWindow
from rpg_narrative_server.domain.narrative.narrative_builder import NarrativeBuilder

logger = logging.getLogger("rpg_narrative_server")


class NarrativeUseCase:
    def __init__(
        self,
        repo,
        llm,
        vector_index,
        event_bus,
        memory_service,
        vector_memory,
        document_resolver,
        context_builder,
    ):
        self.repo = repo
        self.llm = llm
        self.vector_index = vector_index
        self.event_bus = event_bus
        self.memory = memory_service
        self.vector_memory = vector_memory
        self.document_resolver = document_resolver

        self.context_builder = context_builder
        self.narrative_builder = NarrativeBuilder()

        self.context_selector = ContextSelector(max_tokens=1200)
        self.selector = RetrievalSelector()
        self.context_window = DynamicContextWindow()

        self.intent_classifier = IntentClassifier(
            profiles=SUPPORTED_LANGUAGES,
            llm_classifier=LLMIntentClassifier(lambda: self.llm),
        )

    # ---------------------------------------------------------
    # INTERNAL UTILS
    # ---------------------------------------------------------

    def _fallback_response(self, action: str) -> str:
        return f"O mundo reage à sua ação ('{action}'), mas algo permanece incerto..."

    def _handle_task_result(self, task: Task[Any]) -> None:
        if task.cancelled():
            logger.warning("Vector memory task cancelled")
            return

        try:
            exc = task.exception()
        except CancelledError:
            logger.warning("Task cancelled during inspection")
            return
        except Exception as e:
            logger.error("Failed to inspect task", exc_info=e)
            return

        if exc:
            logger.error("Async task failed", exc_info=exc)

    # ---------------------------------------------------------
    # CONTEXT
    # ---------------------------------------------------------

    async def _build_context(
        self, campaign_id: str, action: str, intent: str
    ) -> Tuple[Any, Any]:

        memory_task = asyncio.create_task(self.memory.load_memory(campaign_id))

        k = 4 if intent == "ACTION" else 8 if intent == "EXPLORATION" else 6

        retrieval_task = asyncio.create_task(
            self.vector_index.search_async(action, k=k)
        )

        memory, doc_ids = await asyncio.gather(memory_task, retrieval_task)

        docs = self.document_resolver.resolve(doc_ids)
        docs = self.selector.select(docs)

        policy = self.context_window.get_policy(intent)
        docs = self.context_window.apply(docs, policy)

        docs = self.context_selector.select(docs, self.context_window)
        retrieved = self.selector.extract_texts(docs)

        ctx = await self.context_builder.build(
            campaign_id=campaign_id,
            action=action,
            history=memory.recent_events,
            retrieved=retrieved,
            scene_type=intent,
        )

        return ctx, memory

    # ---------------------------------------------------------
    # PROMPT
    # ---------------------------------------------------------

    def _build_request(self, ctx: Any, action: str, intent: str) -> LLMRequest:
        system_prompt = self.narrative_builder.build_system_prompt(intent)

        user_prompt = self.narrative_builder.build_user_prompt(
            ctx=ctx,
            action=action,
        )

        config = self.narrative_builder.get_generation_config(intent)

        return LLMRequest(
            system_prompt=system_prompt,
            prompt=user_prompt,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
        )

    # ---------------------------------------------------------
    # LLM (robusto + LM Studio safe)
    # ---------------------------------------------------------

    async def _generate_with_retry(
        self,
        request: LLMRequest,
        action: str,
        timeout: float = 180.0,
    ) -> Optional[str]:

        for attempt in range(2):
            try:
                task = asyncio.create_task(self.llm.generate(request))

                try:
                    response = await asyncio.wait_for(task, timeout=timeout)

                except TimeoutError:
                    logger.warning(f"LLM timeout (attempt {attempt + 1})")

                    response = await task

            except Exception:
                logger.exception("LLM error during retry")
                continue

            if not response:
                continue

            cleaned = response.strip()

            # validação de qualidade
            if (
                cleaned.upper() == "OOC"
                or len(cleaned) < 10
                or cleaned.lower() in {"ok", "sim", "não"}
            ):
                logger.warning(f"Bad LLM response (attempt {attempt + 1})")

                if attempt == 0:
                    request.prompt += (
                        "\n\nResponda com pelo menos duas frases narrativas, "
                        "com descrição do ambiente ou consequência da ação."
                    )
                    request.temperature = min(0.9, request.temperature + 0.1)

                continue

            return response

        return None

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    def _is_valid_response(self, response: Optional[str]) -> bool:
        if not response:
            return False

        cleaned = response.strip()

        if len(cleaned) < 20:
            return False

        if cleaned.upper() == "OOC":
            return False

        if cleaned.lower() in {"ok", "sim", "não"}:
            return False

        return True

    # ---------------------------------------------------------
    # EXECUTE
    # ---------------------------------------------------------

    async def execute(self, campaign_id: str, action: str, user_id: str) -> str:
        logger.info(
            "Narrative execution started",
            extra={"campaign_id": campaign_id, "user_id": user_id},
        )

        action = self.narrative_builder.normalize_action(action)

        try:
            intent = await self.intent_classifier.classify(action)

            ctx, memory = await self._build_context(campaign_id, action, intent)

            if not ctx:
                logger.warning("Empty context → fallback")
                return self._fallback_response(action)

            request = self._build_request(ctx, action, intent)

            response = await self._generate_with_retry(request, action)

            if not self._is_valid_response(response):
                logger.warning("Invalid response → fallback")
                response = self._fallback_response(action)

        except CancelledError:
            logger.warning("Narrative execution cancelled")
            raise

        except Exception:
            logger.exception("Fatal error in narrative pipeline")
            return self._fallback_response(action)

        # -------------------------
        # SANITIZE
        # -------------------------

        response = self.narrative_builder.sanitize_output(response)
        response = self.narrative_builder.enforce_length(response, 1200)

        # -------------------------
        # MEMORY
        # -------------------------

        try:
            memory.add_event(action)
            memory.add_event(response)

            await self.memory.save_memory(campaign_id, memory)

        except Exception:
            logger.warning("Memory persistence failed")

        # -------------------------
        # VECTOR MEMORY
        # -------------------------

        try:
            task = asyncio.create_task(
                self.vector_memory.store_event(
                    campaign_id=campaign_id,
                    texts=[action, response],
                    metadata={"type": "event"},
                )
            )
            task.add_done_callback(self._handle_task_result)

        except Exception:
            logger.warning("Vector memory dispatch failed")

        # -------------------------
        # EVENT BUS
        # -------------------------

        try:
            from rpg_narrative_server.domain.events import PlayerActionEvent

            self.event_bus.publish(
                PlayerActionEvent(
                    campaign_id=campaign_id,
                    action=action,
                    user_id=user_id,
                )
            )
        except Exception:
            logger.warning("Event bus failure (ignored)")

        logger.info(
            "Narrative execution completed",
            extra={"campaign_id": campaign_id},
        )

        return response
