from rpg_narrative_server.shared.dice.parser import DiceParser


class DiceParserAdapter:

    def __init__(self):
        self._parser = DiceParser()

    def parse(self, expression: str):
        return self._parser.parse(expression)