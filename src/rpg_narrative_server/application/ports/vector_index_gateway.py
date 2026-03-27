from typing import Protocol, Any


class VectorIndexGateway(Protocol):
    """
    Porta para indexação e busca vetorial.
    """

    async def index_campaign(
        self,
        campaign_id: str,
        texts: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Indexa textos no contexto de uma campanha.
        """
        ...

    async def search(
        self,
        query: str,
        k: int = 4,
    ) -> list[dict]:
        """
        Busca semântica no índice vetorial.

        Returns:
            lista de documentos com pelo menos:
            { "text": str, ... }
        """
        ...
