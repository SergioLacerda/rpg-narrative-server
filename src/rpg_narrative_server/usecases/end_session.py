import asyncio

from rpg_narrative_server.application.dto.llm_request import LLMRequest
from rpg_narrative_server.domain.narrative.session_summarizer import SessionSummarizer


class EndSessionUseCase:
    def __init__(self, memory_service, llm, vector_memory):
        self.memory = memory_service
        self.llm = llm
        self.vector_memory = vector_memory

        self.summarizer = SessionSummarizer()

    def _fallback_summary(self, text: str) -> str:
        return text[:500].strip()

    async def execute(self, campaign_id: str) -> str:
        memory = await self.memory.load_memory(campaign_id)
        events = memory.recent_events

        if not events:
            return "Nenhum evento ocorreu nesta sessão."

        text = self.summarizer.extract([{"text": e} for e in events])

        if not text.strip():
            return "A sessão terminou sem eventos relevantes."

        prompt = self.summarizer.build_prompt(text)

        try:
            response = await self.llm.generate(LLMRequest(prompt=prompt))
            summary = response.content
        except Exception:
            summary = self._fallback_summary(text)

        if not summary.strip():
            summary = self._fallback_summary(text)

        await self.memory.clear(campaign_id)

        asyncio.create_task(
            self.vector_memory.store_event(
                campaign_id=campaign_id,
                texts=[summary],
                metadata={"type": "session_summary"},
            )
        )

        return summary
