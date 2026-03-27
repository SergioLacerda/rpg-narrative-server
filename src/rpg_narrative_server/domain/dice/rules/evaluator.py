from rpg_narrative_server.domain.dice.ast.nodes import (
    RollNode,
    ExplodeNode,
    RerollNode,
    KeepHighestNode,
    DropLowestNode,
)
from .explode import explode
from .reroll import reroll
from .keep_drop import keep_highest, drop_lowest


def evaluate(node, rng):
    if isinstance(node, RollNode):
        return [rng.roll(node.sides) for _ in range(node.quantity)]

    if isinstance(node, ExplodeNode):
        base = evaluate(node.child, rng)
        return explode(base, node.child.sides, rng)

    if isinstance(node, RerollNode):
        base = evaluate(node.child, rng)
        return reroll(base, node.condition, node.child.sides, rng)

    if isinstance(node, KeepHighestNode):
        base = evaluate(node.child, rng)
        return keep_highest(base, node.k)

    if isinstance(node, DropLowestNode):
        base = evaluate(node.child, rng)
        return drop_lowest(base, node.k)

    raise ValueError(f"Unknown node: {node}")
