from typing import List

BASE_BITS = 5


class Position:

    def __init__(self, pos: List[int]=None, base_bits: int=0) -> None:
        # Holds tree path as variable base digits of size 2^(BASE_BITS + el.
        # no)
        self.pos = pos or []
        self.base_bits = base_bits or BASE_BITS

    @classmethod
    def from_int(cls, i: int, depth: int) -> "Position":
        new_pos = cls()
        tmp = i

        for d in range(depth, 0, -1):
            shift = BASE_BITS + d - 1
            # Extract n rightmost bits where n equals the no. of bits at depth
            # `d`
            new_pos.pos.insert(0, tmp & (1 << shift) - 1)
            tmp = tmp >> shift

        return new_pos

    def to_int(self, trim: int=0) -> int:
        def ptrim(l, depth):
            out = []
            length = len(l)
            for d in range(depth):
                if d < length:
                    out.append(l[d])
                else:
                    out.append(0)

            return out

        if trim:
            workspace = ptrim(self.pos, trim)
        else:
            workspace = self.pos

        out = 0
        for d, i in enumerate(workspace):
            # Add zeros and place `i` in them
            out = (out << (self.base_bits + d)) | int(i)

        return out

    def interval_between(self, other: "Position", depth: int) -> int:
        return other.to_int(depth) - self.to_int(depth) - 1

    def __lt__(self, other):
        return self.pos < other.pos

    def __str__(self):
        return str(self.pos)
