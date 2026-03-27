import pytest


def test_chroma_backend_builds():
    pytest.importorskip("chromadb")

    from rpg_narrative_server.infrastructure.storage.backends.chroma_backend import (
        ChromaStorageBackend,
    )

    backend = ChromaStorageBackend()

    assert backend.build_vector_store() is not None
