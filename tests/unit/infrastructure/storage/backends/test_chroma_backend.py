import pytest

pytest.importorskip("chromadb")


def test_chroma_backend_builds():

    from rpg_narrative_server.infrastructure.storage.backends.chroma_backend import (
        ChromaStorageBackend,
    )

    backend = ChromaStorageBackend()

    assert backend.build_vector_store() is not None
    assert backend.build_document_store() is not None
    assert backend.build_token_store() is not None
    assert backend.build_metadata_store() is not None
