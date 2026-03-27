from typing import List, Dict


class VectorMemoryPort:
    """
    Porta para escrita no sistema vetorial (RAG write-side)
    """

    async def store_event(
        self,
        campaign_id: str,
        texts: List[str],
        metadata: Dict,
    ):
        raise NotImplementedError
