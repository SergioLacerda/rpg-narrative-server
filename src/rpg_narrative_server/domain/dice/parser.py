from rpg_narrative_server.shared.dice.dice_regex import DiceRegex
from rpg_narrative_server.domain.dice.condition import _Condition
from rpg_narrative_server.domain.dice.ast.nodes import (
    DiceCondition,
    DiceNode,
    RollNode,
    ExplodeNode,
    RerollNode,
    KeepHighestNode,
    DropLowestNode,
)


class DiceParser:
    def _build_condition(self, cond: str) -> DiceCondition:
        return _Condition(cond)

    def parse(self, expression: str) -> DiceNode:
        match = DiceRegex.match(expression)

        if not match:
            raise ValueError(f"Invalid dice expression: {expression}")

        # -------------------------
        # BASE
        # -------------------------
        num = int(match.group("num"))
        sides = int(match.group("sides"))

        node: DiceNode = RollNode(num, sides)

        # -------------------------
        # EXPLODE (!)
        # -------------------------
        if match.group("explode"):
            node = ExplodeNode(node)

        # -------------------------
        # KEEP (khX)
        # -------------------------
        keep = match.group("keep")
        if keep:
            try:
                k = int(keep[2:])
                node = KeepHighestNode(node, k)
            except ValueError:
                raise ValueError(f"Invalid keep modifier: {keep}")

        # -------------------------
        # DROP (dlX)
        # -------------------------
        drop = match.group("drop")
        if drop:
            try:
                k = int(drop[2:])
                node = DropLowestNode(node, k)
            except ValueError:
                raise ValueError(f"Invalid drop modifier: {drop}")

        # -------------------------
        # REROLL (r<3, r>=2, etc)
        # -------------------------
        reroll = match.group("reroll")
        if reroll:
            node = RerollNode(node, self._build_condition(reroll))

        return node

    # --------------------------------------------------
    # CONDITION BUILDER
    # --------------------------------------------------
