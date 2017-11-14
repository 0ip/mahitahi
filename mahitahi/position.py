from typing import List, Tuple

BASE_BITS = 5


class Position:

    def __init__(self, pos: List[int]=None, sites: List[int]=None, base_bits: int=0) -> None:
        # Each element is part of the tree path as a var. base digit of size 2^(BASE_BITS + el. no)
        self.pos = pos or []
        self.sites = sites or []
        self.base_bits = base_bits or BASE_BITS

    @classmethod
    def from_int(cls, pos: int, depth: int, sites: List[int], base_bits: int=0) -> "Position":
        new_pos = cls(sites=sites, base_bits=base_bits)

        for _depth in range(depth, 0, -1):
            shift = base_bits + _depth - 1
            # Extract n rightmost bits where n equals the no. of bits at depth `_depth`
            new_pos.pos.insert(0, pos & (1 << shift) - 1)
            pos >>= shift

        return new_pos

    def to_int(self, trim: int=0) -> int:
        if trim:
            workspace = self._ptrim(self.pos, trim)
        else:
            workspace = self.pos

        out = 0
        for _depth, i in enumerate(workspace):
            # Add zeros and place `i` in them
            out = (out << (self.base_bits + _depth)) | int(i)

        return out

    def interval_between(self, other: "Position", depth: int) -> Tuple[int, bool]:
        if self.pos == other.pos and self.sites[-1] != other.sites[-1] and depth > len(self.pos):
            return self.interval_at(depth), True

        return other.to_int(depth) - self.to_int(depth) - 1, False

    def interval_at(self, depth: int) -> int:
        return 2 ** (self.base_bits + depth - 1) - 1

    @staticmethod
    def _ptrim(pos: List[int], depth: int) -> List[int]:
        out = []
        length = len(pos)
        for _depth in range(depth):
            if _depth < length:
                out.append(pos[_depth])
            else:
                out.append(0)

        return out

    def __lt__(self, other):
        # Lexical order by `position` and `site` as tie-breaker
        return list(zip(self.pos, self.sites)) < list(zip(other.pos, other.sites))

    def __str__(self):
        return str(list(zip(self.pos, self.sites)))
