from rpg_narrative_server.domain.narrative.narrative_memory import NarrativeMemory
from rpg_narrative_server.application.dto.llm_request import LLMRequest


class MemoryService:
    def __init__(
        self,
        repository,
        *,
        max_events: int = 10,
        summarizer=None,
        llm_service=None,
        compressor=None,
    ):
        self.repo = repository
        self.max_events = max_events
        self.summarizer = summarizer
        self.llm = llm_service
        self.compressor = compressor or self._default_compress

    # ---------------------------------------------------------

    async def load_memory(self, campaign_id: str) -> NarrativeMemory:
        data = await self.repo.get_events(campaign_id)

        if not data:
            return NarrativeMemory()

        memory = NarrativeMemory()
        memory.recent_events = [e.get("text", "") for e in data]

        return memory

    # ---------------------------------------------------------

    async def save_memory(self, campaign_id: str, memory: NarrativeMemory):
        events = [{"text": e} for e in memory.recent_events]

        await self.repo.save_events(campaign_id, events)

    # ---------------------------------------------------------

    async def append(self, campaign_id: str, text: str):
        text = self.compressor(text)

        if not text:
            return

        memory = await self.load_memory(campaign_id)

        memory.add_event(text)

        if len(memory.recent_events) > self.max_events:
            overflow = memory.recent_events[: -self.max_events]
            recent = memory.recent_events[-self.max_events :]

            if self.summarizer and len(overflow) >= 3:
                raw_text = self.summarizer.extract([{"text": e} for e in overflow])

                if self.llm:
                    prompt = self.summarizer.build_prompt(raw_text)

                    request = LLMRequest(
                        prompt=prompt,
                        system_prompt="",
                        temperature=0.3,
                        max_tokens=300,
                    )

                    response = await self.llm.generate(request)

                    summary = response or memory.summary

                else:
                    summary = (memory.summary + "\n" + raw_text).strip()

                    if len(summary) > 1000:
                        summary = summary[-1000:]

                memory.update_summary(summary)

            memory.recent_events = recent

        await self.save_memory(campaign_id, memory)

    # ---------------------------------------------------------

    async def clear(self, campaign_id: str):
        await self.repo.save_events(campaign_id, [])

    # ---------------------------------------------------------

    def _default_compress(self, text: str) -> str:
        if not text:
            return text

        text = text.strip()

        if len(text) > 200:
            return text[:200].rsplit(" ", 1)[0]

        return text
