# domain/dice/rules.py
from .value_objects import DiceExpression
from rpg_narrative_server.domain.random.random_provider import RandomProvider

def roll_dice(expr: DiceExpression, rng: RandomProvider) -> int:
    total = 0

    for _ in range(expr.quantity):
        value = rng.roll(expr.sides)
        total += value

    return total + expr.modifier