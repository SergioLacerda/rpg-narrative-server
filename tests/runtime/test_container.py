import pytest

from rpg_narrative_server.application.dto.llm_request import LLMRequest
from tests.config.builders.test_container_builder import TestContainerBuilder
from tests.config.fakes.fake_llm import FakeLLMService


def test_container_builds_core(container):
    assert container.embedding is not None
    assert container.vector_index is not None

    assert isinstance(container.llm, FakeLLMService)


def test_container_lazy_loading():
    c = TestContainerBuilder().build()

    first = c.llm
    second = c.llm

    assert first is second


def test_narrative_usecase_wiring(container):
    usecase = container.narrative

    assert usecase is not None
    assert usecase.llm is not None
    assert usecase.vector_index is not None

    assert isinstance(usecase.llm, FakeLLMService)


@pytest.mark.asyncio
async def test_llm_integration(container):
    assert isinstance(container.llm, FakeLLMService)

    response = await container.llm.generate(LLMRequest(prompt="teste"))

    assert response is not None
