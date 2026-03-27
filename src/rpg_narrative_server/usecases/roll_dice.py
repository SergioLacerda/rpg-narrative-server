from rpg_narrative_server.application.ports.dice_parser import DiceParserPort

from rpg_narrative_server.domain.dice.dice_engine import roll
from rpg_narrative_server.domain.dice.probability import analyze_distribution
from rpg_narrative_server.domain.dice.value_objects import DiceExpression
from rpg_narrative_server.domain.dice.ast.nodes import RollNode


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

    async def execute(self, expression):
        try:
            if isinstance(expression, DiceExpression):
                ast = RollNode(expression.quantity, expression.sides)

            elif isinstance(expression, str):
                ast = self.parser.parse(expression)

                if ast is None:
                    return {"error": "Invalid dice expression"}

            elif hasattr(expression, "evaluate"):
                ast = expression

            else:
                return {"error": "Invalid dice expression"}

        except (ValueError, SyntaxError):
            return {"error": "Invalid dice expression"}

        try:
            rolls, total = roll(ast, self.rng)
        except Exception:
            return {"error": "Roll execution failed"}

        result = {
            "rolls": rolls,
            "total": total,
        }

        if self.enable_analysis:
            try:
                result["distribution"] = analyze_distribution(ast)
            except Exception:
                result["distribution"] = None

        return result
