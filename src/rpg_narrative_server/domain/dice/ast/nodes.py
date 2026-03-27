from dataclasses import dataclass
from typing import Protocol


# ---------------------------------------------------------
# BASE NODE (AST)
# ---------------------------------------------------------


class DiceNode:
    """
    Base class for all dice AST nodes.
    """

    pass


# ---------------------------------------------------------
# CONDITION PROTOCOL
# ---------------------------------------------------------


class DiceCondition(Protocol):
    def __call__(self, value: int) -> bool: ...


# ---------------------------------------------------------
# NODES
# ---------------------------------------------------------


@dataclass(slots=True)
class RollNode(DiceNode):
    quantity: int
    sides: int


@dataclass(slots=True)
class ExplodeNode(DiceNode):
    child: DiceNode


@dataclass(slots=True)
class RerollNode(DiceNode):
    child: DiceNode
    condition: DiceCondition


@dataclass(slots=True)
class KeepHighestNode(DiceNode):
    child: DiceNode
    k: int


@dataclass(slots=True)
class DropLowestNode(DiceNode):
    child: DiceNode
    k: int
