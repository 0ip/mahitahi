from abc import ABC, abstractmethod
from random import randint, getrandbits


class Strategy(ABC):

    @abstractmethod
    def for_depth(self, depth: int):
        pass


class RandomStrategy(Strategy):

    def __init__(self):
        self._history: Dict[int, bool] = {}  # <depth, boundary[+|-]>

    def for_depth(self, depth: int):
        if depth not in self._history:
            self._history[depth] = bool(getrandbits(1))

        return self._history[depth]


class RoundRobinStrategy(Strategy):

    def for_depth(self, depth: int):
        return depth % 2
