import logging

from rpg_narrative_server.application.contracts.response import Response
from rpg_narrative_server.application.dto.llm_request import LLMRequest
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
        intent_classifier=None,
        narrative_builder=None,
    ):
        self.repo = repo
        self.llm = llm
        self.vector_index = vector_index
        self.event_bus = event_bus
        self.memory = memory_service
        self.vector_memory = vector_memory
        self.document_resolver = document_resolver
        self.context_builder = context_builder

        self.intent_classifier = intent_classifier or self._default_intent()
        self.narrative_builder = narrative_builder or NarrativeBuilder()

    def _default_intent(self):
        class DummyIntent:
            async def classify(self, *_):
                return "DEFAULT"

        return DummyIntent()

    def _fallback_response(self, action: str, intent: str) -> Response:
        return Response(
            text=f"O mundo reage à sua ação ('{action}'), mas algo permanece incerto...",
            type="narrative",
            metadata={
                "intent": intent,
                "fallback": True,
            },
        )

    # ---------------------------------------------------------
    # EXECUTE
    # ---------------------------------------------------------

    async def execute(self, campaign_id: str, action: str, user_id: str):
        logger.info("Narrative execution started")

        # -------------------------------------------------
        # 0. INTENT
        # -------------------------------------------------
        intent = await self.intent_classifier.classify(action)

        # -------------------------------------------------
        # 1. CONTEXT
        # -------------------------------------------------
        ctx, memory = await self.context_builder.build(
            campaign_id=campaign_id,
            action=action,
            intent=intent,
        )

        builder = self.narrative_builder
        scene = ctx.get("scene_type")

        # -------------------------------------------------
        # 2. PROMPT
        # -------------------------------------------------
        system_prompt = builder.build_system_prompt(scene_type=scene)

        user_prompt = builder.build_user_prompt(
            ctx=ctx,
            action=action,
        )

        config = builder.get_generation_config(scene)

        request = LLMRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=config["temperature"],
            max_tokens=int(config["max_tokens"]),
            metadata={
                "intent": intent,
                "scene_type": scene,
            },
        )

        # -------------------------------------------------
        # 3. LLM
        # -------------------------------------------------
        try:
            response = await self.llm.generate(request)
        except Exception:
            logger.warning("LLM failed", exc_info=True)
            return self._fallback_response(action, intent)

        if response is None:
            raise RuntimeError("LLM returned None")

        content = getattr(response, "content", None)

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("LLM returned empty content")

        # -------------------------------------------------
        # 4. OUTPUT
        # -------------------------------------------------
        text = builder.sanitize_output(content)

        return Response(
            text=text,
            type="narrative",
            metadata={
                "intent": intent,
                "scene_type": scene,
            },
        )
