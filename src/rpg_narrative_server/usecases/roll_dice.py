from rpg_narrative_server.application.contracts.response import Response
from rpg_narrative_server.application.ports.dice_parser import DiceParserPort
from rpg_narrative_server.domain.dice.ast.nodes import RollNode
from rpg_narrative_server.domain.dice.dice_engine import roll
from rpg_narrative_server.domain.dice.probability import analyze_distribution
from rpg_narrative_server.domain.dice.value_objects import DiceExpression


class RollDiceUseCase:
    def __init__(
        self,
        rng,
        parser: DiceParserPort,
        enable_analysis: bool = False,
    ):
        self.rng = rng
        self.parser = parser
        self.enable_analysis = enable_analysis

    async def execute(self, expression) -> Response:
        try:
            if isinstance(expression, DiceExpression):
                ast = RollNode(expression.quantity, expression.sides)

            elif isinstance(expression, str):
                ast = self.parser.parse(expression)
                if ast is None:
                    return self._error("Invalid dice expression")

            elif hasattr(expression, "evaluate"):
                ast = expression

            else:
                return self._error("Invalid dice expression")

        except (ValueError, SyntaxError):
            return self._error("Invalid dice expression")

        try:
            rolls, total = roll(ast, self.rng)
        except Exception:
            return self._error("Roll execution failed")

        data = {
            "rolls": rolls,
            "total": total,
        }

        if self.enable_analysis:
            try:
                data["distribution"] = analyze_distribution(ast)
            except Exception:
                data["distribution"] = None

        return Response(
            text=self._format_text(data),
            type="dice",
            metadata=data,
        )

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def _error(self, message: str) -> Response:
        return Response(
            text=message,
            type="error",
            metadata={"error": message},
        )

    def _format_text(self, data: dict) -> str:
        rolls = ", ".join(map(str, data["rolls"]))
        total = data["total"]

        return f"🎲 Rolls: [{rolls}] → Total: {total}"
