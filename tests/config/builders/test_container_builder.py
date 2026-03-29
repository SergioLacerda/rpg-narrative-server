# tests/config/builders/test_container_builder.py

from rpg_narrative_server.bootstrap.container_builder import ContainerBuilder
from tests.config.fakes.fake_embedding import FakeEmbeddingProvider
from tests.config.fakes.fake_llm import FakeLLMService
from tests.config.fakes.fake_vector_index import FakeVectorIndex


class TestContainerBuilder:
    """
    Builder exclusivo para testes.

    - Nunca deve existir no código produtivo
    - Injeta fakes por padrão
    """

    def __init__(self):
        self._builder = ContainerBuilder().with_profile("test")

        self._llm = FakeLLMService()
        self._embedding = FakeEmbeddingProvider()
        self._vector_index = FakeVectorIndex()

    # ---------------------------------------------------------
    # OVERRIDES
    # ---------------------------------------------------------
    def with_llm(self, llm):
        self._llm = llm
        return self

    def with_embedding(self, embedding):
        self._embedding = embedding
        return self

    def with_vector_index(self, vector_index):
        self._vector_index = vector_index
        return self

    # ---------------------------------------------------------
    # BUILD
    # ---------------------------------------------------------
    def build(self):
        return (
            self._builder.with_llm(self._llm)
            .with_embedding(self._embedding)
            .with_vector_index(self._vector_index)
            .build()
        )
