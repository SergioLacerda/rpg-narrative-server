import pytest

from rpg_narrative_server.application.dto.llm_request import LLMRequest

from tests.config.fakes.fake_llm import FakeLLMService

@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_basic_flow(container):

    result = await container.narrative.execute(
        user_id="user1",
        campaign_id="test_campaign",
        action="look around"
    )

    assert isinstance(result, str)
    assert result.strip() != ""


@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_uses_memory(container):

    usecase = container.narrative

    first = await usecase.execute(
        user_id="user1",
        campaign_id="test",
        action="open door"
    )

    second = await usecase.execute(
        user_id="user1",
        campaign_id="test",
        action="enter room"
    )

    assert second != first


@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_llm_failure(container_factory):

    fake = FakeLLMService(fail=True)

    container = container_factory(llm=fake)

    result = await container.narrative.execute(
        user_id="1",
        campaign_id="test",
        action="test"
    )

    assert isinstance(result, str)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_event_bus_failure(container, monkeypatch):

    def fail(*args, **kwargs):
        raise Exception("event bus failed")

    monkeypatch.setattr(container.event_bus, "publish", fail)

    result = await container.narrative.execute(
        campaign_id="test",
        action="test",
        user_id="user"
    )

    assert isinstance(result, str)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_same_input_generates_valid_output(container):

    result1 = await container.narrative.execute(
        user_id="user",
        campaign_id="test",
        action="wait"
    )

    result2 = await container.narrative.execute(
        user_id="user",
        campaign_id="test",
        action="wait"
    )

    assert isinstance(result1, str)
    assert isinstance(result2, str)


@pytest.mark.asyncio
async def test_narrative_snapshot(container_factory):

    fake_llm = FakeLLMService()

    container = container_factory(llm=fake_llm)

    result = await container.narrative.execute(
        user_id="user",
        campaign_id="test",
        action="look around"
    )

    assert "look" in result.lower()
    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_narrative_multi_step_flow(container):

    usecase = container.narrative

    await usecase.execute(user_id="u", campaign_id="c", action="look")
    await usecase.execute(user_id="u", campaign_id="c", action="walk")
    result = await usecase.execute(user_id="u", campaign_id="c", action="open door")

    assert isinstance(result, str)