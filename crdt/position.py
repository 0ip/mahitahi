from typing import List


class Position:
    BASE_BITS = 5

    def __init__(self, pos: List[int]=None) -> None:
        self.pos = pos or []  # Holds tree path as variable base digits of size 2^(BASE_BITS + el. no)

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
            out = (out << (self.BASE_BITS + d)) | int(i)  # Add zeros and place `i` in them

        return out

    @classmethod
    def from_int(cls, i: int, depth: int) -> "Position":
        new_pos = cls()
        tmp = i

        for d in range(depth, 0, -1):
            shift = cls.BASE_BITS + d - 1
            # Extract n rightmost bits where n equals the no. of bits at depth `d`
            new_pos.pos.insert(0, tmp & (1 << shift) - 1)
            tmp = tmp >> shift

        return new_pos

    def interval_between(self, other: "Position", depth: int) -> int:
        return other.to_int(depth) - self.to_int(depth) - 1

    def __lt__(self, other):
        return self.pos < other.pos

    def __str__(self):
        return str(self.pos)
