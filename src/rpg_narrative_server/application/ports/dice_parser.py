from typing import Protocol


class DiceParserPort(Protocol):
    def parse(self, expression: str): ...
