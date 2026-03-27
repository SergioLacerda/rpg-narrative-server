from tests.config.fakes.fake_llm import FakeLLMService
from tests.config.fakes.fake_embedding import FakeEmbeddingProvider
from tests.config.fakes.fake_vector_index import FakeVectorIndex


def create_test_container(llm=None):
    from rpg_narrative_server.bootstrap.container import Container

    container = Container()

    container._llm_service = llm or FakeLLMService()
    container._embedding = FakeEmbeddingProvider()
    container._vector_index = FakeVectorIndex()

    container._intent_classifier = None

    return container
