from rpg_narrative_server.bootstrap.container_builder import ContainerBuilder
from tests.config.fakes.fake_embedding import FakeEmbeddingProvider
from tests.config.fakes.fake_llm import FakeLLMService
from tests.config.fakes.fake_vector_index import FakeVectorIndex


def create_test_container(llm=None):
    return (
        ContainerBuilder()
        .with_profile("test")
        .with_llm(llm or FakeLLMService())
        .with_embedding(FakeEmbeddingProvider())
        .with_vector_index(FakeVectorIndex())
        .build()
    )
