import pytest

from rpg_narrative_server.infrastructure.storage.backends.base import StorageBackend


class DummyBackend(StorageBackend):
    def build_vector_store(self):
        return super().build_vector_store()

    def build_document_store(self):
        return super().build_document_store()

    def build_token_store(self):
        return super().build_token_store()

    def build_metadata_store(self):
        return super().build_metadata_store()


def test_abstract_methods():
    backend = DummyBackend()

    with pytest.raises(NotImplementedError):
        backend.build_vector_store()

    with pytest.raises(NotImplementedError):
        backend.build_document_store()

    with pytest.raises(NotImplementedError):
        backend.build_token_store()

    with pytest.raises(NotImplementedError):
        backend.build_metadata_store()


def test_base_backend_not_implemented():
    backend = DummyBackend()

    with pytest.raises(NotImplementedError):
        backend.build_vector_store()

    with pytest.raises(NotImplementedError):
        backend.build_document_store()

    with pytest.raises(NotImplementedError):
        backend.build_token_store()

    with pytest.raises(NotImplementedError):
        backend.build_metadata_store()
