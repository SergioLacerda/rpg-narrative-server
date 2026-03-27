from rpg_narrative_server.shared.dice.dice_regex import DiceRegex

from rpg_narrative_server.domain.dice.ast.nodes import (
    RollNode,
    ExplodeNode,
    RerollNode,
    KeepHighestNode,
    DropLowestNode,
)


class DiceParser:
    def parse(self, expression: str):
        match = DiceRegex.match(expression)

        if not match:
            raise ValueError("Invalid dice expression")

        num = int(match.group("num"))
        sides = int(match.group("sides"))

        node = RollNode(num, sides)

        # explode
        if match.group("explode"):
            node = ExplodeNode(node)

        # keep
        if match.group("keep"):
            k = int(match.group("keep")[2:])
            node = KeepHighestNode(node, k)

        # drop
        if match.group("drop"):
            k = int(match.group("drop")[2:])
            node = DropLowestNode(node, k)

        # reroll
        if match.group("reroll"):
            cond = match.group("reroll")
            node = RerollNode(node, self._build_condition(cond))

        return node

    # --------------------------------------------------
    # PRIVATE
    # --------------------------------------------------

    def _build_condition(self, cond: str):
        def condition(v: int):
            if "<=" in cond:
                return v <= int(cond.split("<=")[1])

            if ">=" in cond:
                return v >= int(cond.split(">=")[1])

            if "<" in cond:
                return v < int(cond.split("<")[1])

            if ">" in cond:
                return v > int(cond.split(">")[1])

            return False

        return condition
