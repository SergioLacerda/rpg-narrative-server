import pytest

from rpg_narrative_server.bootstrap.container import Container
from rpg_narrative_server.application.dto.llm_request import LLMRequest

from tests.config.fakes.fake_llm import FakeLLMService
def test_container_builds_core(container):

    assert container.embedding is not None
    assert container.vector_index is not None
    assert container.llm is not None


def test_container_lazy_loading():

    c = Container()

    assert c._llm_service is None

    c._build_llm_service = lambda: FakeLLMService()

    _ = c.llm

    assert c._llm_service is not None


def test_narrative_usecase_wiring(container):

    usecase = container.narrative

    assert usecase is not None
    assert usecase.llm is not None
    assert usecase.vector_index is not None


@pytest.mark.asyncio
async def test_llm_integration(container):


    response = await container.llm.generate(
        LLMRequest(prompt="teste")
    )

    assert response is not None