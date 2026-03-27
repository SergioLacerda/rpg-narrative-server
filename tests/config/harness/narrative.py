# tests/config/harness/narrative.py

class NarrativeHarness:

    def __init__(self, *, llm_result="ok"):

        from tests.config.fakes.fake_llm import FakeLLMService
        from tests.config.fakes.fake_vector_index import FakeVectorIndex

        self.llm = FakeLLMService(result=llm_result)
        self.vector_index = FakeVectorIndex()

        self.calls = []

    def build(self, container_factory):
        self.container = container_factory(
            llm=self.llm,
            vector_index=self.vector_index
        )
        return self.container.narrative

    async def run(self, action="look", campaign_id="test", user_id="u1"):
        usecase = self.container.narrative

        result = await usecase.execute(
            campaign_id=campaign_id,
            action=action,
            user_id=user_id,
        )

        self.calls.append({
            "action": action,
            "result": result
        })

        return result