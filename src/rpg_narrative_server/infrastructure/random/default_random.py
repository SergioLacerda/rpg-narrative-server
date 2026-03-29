import random

from rpg_narrative_server.domain.random.random_provider import RandomProvider


class DefaultRandomProvider(RandomProvider):
    def roll(self, sides: int) -> int:
        return random.randint(1, sides)
