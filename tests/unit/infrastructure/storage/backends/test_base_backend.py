import pytest

from rpg_narrative_server.infrastructure.storage.backends.base import StorageBackend


class IncompleteBackend(StorageBackend):
    pass


class DummyBackend(StorageBackend):
    def build_vector_store(self):
        return "vector"

    def build_document_store(self):
        return "doc"

    def build_token_store(self):
        return "token"

    def build_metadata_store(self):
        return "meta"


def test_storage_backend_contract():
    backend = DummyBackend()

    assert backend.build_vector_store() == "vector"
    assert backend.build_document_store() == "doc"
    assert backend.build_token_store() == "token"
    assert backend.build_metadata_store() == "meta"


def test_storage_backend_is_abstract():
    with pytest.raises(TypeError):
        StorageBackend()  # type: ignore[abstract]


def test_incomplete_backend_fails():
    with pytest.raises(TypeError):
        IncompleteBackend()  # type: ignore[abstract]
