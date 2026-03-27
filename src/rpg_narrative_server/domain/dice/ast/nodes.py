from dataclasses import dataclass
from typing import Callable


class DiceNode:
    pass


@dataclass
class RollNode(DiceNode):
    quantity: int
    sides: int


@dataclass
class ExplodeNode(DiceNode):
    child: DiceNode


@dataclass
class RerollNode(DiceNode):
    child: DiceNode
    condition: Callable[[int], bool]


@dataclass
class KeepHighestNode(DiceNode):
    child: DiceNode
    k: int


@dataclass
class DropLowestNode(DiceNode):
    child: DiceNode
    k: int