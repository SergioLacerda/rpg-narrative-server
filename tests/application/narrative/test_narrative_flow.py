import pytest

from rpg_narrative_server.application.contracts.response import Response
from tests.config.fakes.fake_llm import FakeLLMService
from tests.config.helpers.asserts import assert_contains, assert_not_empty


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_basic_flow(container):
    result = await container.narrative.execute(
        user_id="user1",
        campaign_id="test_campaign",
        action="look around",
    )

    assert isinstance(result, Response)
    assert isinstance(result.text, str)
    assert_not_empty(result)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_uses_memory(container):
    usecase = container.narrative

    first = await usecase.execute(user_id="user1", campaign_id="test", action="open door")

    second = await usecase.execute(user_id="user1", campaign_id="test", action="enter room")

    assert second != first


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_llm_failure(container_factory):
    fake = FakeLLMService(fail=True)

    container = container_factory(llm=fake)

    result = await container.narrative.execute(user_id="1", campaign_id="test", action="test")

    assert isinstance(result, Response)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_event_bus_failure(container, monkeypatch):
    def fail(*args, **kwargs):
        raise Exception("event bus failed")

    monkeypatch.setattr(container.event_bus, "publish", fail)

    result = await container.narrative.execute(campaign_id="test", action="test", user_id="user")

    assert isinstance(result, Response)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_same_input_generates_valid_output(container):
    result1 = await container.narrative.execute(
        user_id="user",
        campaign_id="test",
        action="wait",
    )

    result2 = await container.narrative.execute(
        user_id="user",
        campaign_id="test",
        action="wait",
    )

    assert isinstance(result1, Response)
    assert isinstance(result1.text, str)

    assert isinstance(result2, Response)
    assert isinstance(result2.text, str)

    assert result1.text != ""
    assert result2.text != ""


@pytest.mark.asyncio
async def test_narrative_snapshot(container_factory):
    fake_llm = FakeLLMService()

    container = container_factory(llm=fake_llm)

    result = await container.narrative.execute(
        user_id="user", campaign_id="test", action="look around"
    )

    assert_contains(result, "look")
    assert result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_narrative_multi_step_flow(container):
    usecase = container.narrative

    await usecase.execute(user_id="u", campaign_id="c", action="look")
    await usecase.execute(user_id="u", campaign_id="c", action="walk")
    result = await usecase.execute(user_id="u", campaign_id="c", action="open door")

    assert isinstance(result, Response)
