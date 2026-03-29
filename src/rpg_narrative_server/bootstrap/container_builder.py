# container_builder.py

from rpg_narrative_server.bootstrap.container import Container


class ContainerBuilder:
    def __init__(self):
        self._overrides = {}
        self._profile = "default"

    # ---------------------------------------------------------
    # PROFILE
    # ---------------------------------------------------------
    def with_profile(self, profile: str):
        self._profile = profile
        return self

    # ---------------------------------------------------------
    # OVERRIDES
    # ---------------------------------------------------------
    def with_llm(self, llm):
        self._overrides["llm"] = llm
        return self

    def with_embedding(self, embedding):
        self._overrides["embedding"] = embedding
        return self

    def with_vector_index(self, vector_index):
        self._overrides["vector_index"] = vector_index
        return self

    # ---------------------------------------------------------
    # BUILD
    # ---------------------------------------------------------
    def build(self):
        container = Container()

        # ----------------------------------
        # PROFILE
        # ----------------------------------
        self._apply_profile(container)

        # ----------------------------------
        # OVERRIDES
        # ----------------------------------
        if "llm" in self._overrides:
            container._llm_service = self._overrides["llm"]

        if "embedding" in self._overrides:
            container._embedding = self._overrides["embedding"]

        if "vector_index" in self._overrides:
            container._vector_index = self._overrides["vector_index"]

        return container

    # ---------------------------------------------------------
    # PROFILE LOGIC
    # ---------------------------------------------------------
    def _apply_profile(self, container):
        if self._profile == "test":
            self._apply_test_profile(container)

        elif self._profile == "dev":
            pass

        elif self._profile == "prod":
            pass

    # ---------------------------------------------------------
    def _apply_test_profile(self, container):
        # desabilitar caches pesados
        container._response_cache = None
        container._ttl_cache = None
