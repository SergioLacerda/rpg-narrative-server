from typing import Optional, Dict, Any

from rpg_narrative_server.vector_index.components import DocumentStore


class DocumentStoreAdapter(DocumentStore):
    """
    Adapter que conecta um KV store genérico ao contrato DocumentStore.

    ✔ Implementa o Protocol (Clean Arch)
    ✔ Isola infra (KV store) do domínio
    ✔ Substituível (JSON, Redis, Memory, etc)
    """

    def __init__(self, kv_store):
        self._store = kv_store

    # ---------------------------------------------------------
    # API
    # ---------------------------------------------------------

    def set(self, doc_id: str, document: Dict[str, Any]) -> None:
        if not doc_id:
            raise ValueError("doc_id cannot be empty")

        if not isinstance(document, dict):
            raise TypeError("document must be a dict")

        self._store.set(doc_id, document)

    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        if not doc_id:
            return None

        return self._store.get(doc_id)

    # ---------------------------------------------------------
    # opcional (debug / manutenção)
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Limpa o store se suportado.
        """
        if hasattr(self._store, "clear"):
            self._store.clear()