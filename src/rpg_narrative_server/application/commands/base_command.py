from abc import ABC, abstractmethod
from typing import Any


class BaseCommand(ABC):
    """
    Interface base para todos os comandos da aplicação.

    NÃO depende de framework (Discord, HTTP, etc)
    """

    name: str

    @abstractmethod
    async def execute(self, ctx: Any, **kwargs) -> Any:
        """
        Executa o comando.

        Retorna:
        - str
        - Response
        - ou outro objeto serializável
        """
        raise NotImplementedError
