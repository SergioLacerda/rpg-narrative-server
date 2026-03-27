from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def build_vector_store(self):
        raise NotImplementedError

    @abstractmethod
    def build_document_store(self):
        raise NotImplementedError

    @abstractmethod
    def build_token_store(self):
        raise NotImplementedError

    @abstractmethod
    def build_metadata_store(self):
        raise NotImplementedError
