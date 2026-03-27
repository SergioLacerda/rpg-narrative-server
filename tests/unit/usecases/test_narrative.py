import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_basic_flow(container):
    result = await container.narrative.execute(
        user_id="user1", campaign_id="test_campaign", action="look around"
    )

    assert isinstance(result, str)
    assert result.strip() != ""


@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_llm_failure(container_factory):
    class FailingLLM:
        async def generate(self, prompt):
            raise Exception("LLM failed")

    container = container_factory(llm=FailingLLM())

    result = await container.narrative.execute(
        user_id="1", campaign_id="test", action="test"
    )

    assert isinstance(result, str)
    assert result.strip() != ""


@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_event_bus_failure(container, monkeypatch):
    def fail(*args, **kwargs):
        raise Exception("event bus failed")

    monkeypatch.setattr(container.event_bus, "publish", fail)

    result = await container.narrative.execute(
        campaign_id="test", action="test", user_id="user"
    )

    assert isinstance(result, str)
    assert result.strip() != ""
