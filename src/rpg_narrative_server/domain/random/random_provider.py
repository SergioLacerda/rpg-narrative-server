from abc import ABC, abstractmethod


class RandomProvider(ABC):
    @abstractmethod
    def roll(self, sides: int) -> int:
        pass