import json

from sortedcontainers import SortedList
from random import randint
from typing import Dict, Sequence

from .char import Char
from .position import Position, BASE_BITS
from .strategy import RandomStrategy


class CRDTDoc:

    BOUNDARY = 5

    def __init__(self, site: int=0) -> None:
        self.site: int = site

        self._strategy = RandomStrategy()
        self._clock: int = 0
        self._doc: SortedList["Char"] = SortedList()
        self._doc.add(Char("", Position([0], [-1]), self._clock))
        self._doc.add(Char("", Position([2 ** BASE_BITS - 1], [-1]), self._clock))

    def insert(self, pos: int, char: str) -> str:
        self._clock += 1
        p, q = self._doc[pos].pos, self._doc[pos + 1].pos

        new_char = Char(char, self._alloc(p, q), self._clock)
        self._doc.add(new_char)

        return self._serialize("i", new_char)

    def delete(self, pos: int) -> str:
        self._clock += 1
        old_char = self._doc[pos + 1]
        self._doc.remove(old_char)

        return self._serialize("d", old_char)

    def _alloc(self, p: "Position", q: "Position") -> "Position":
        depth = 0
        interval = 0
        equal = False
        while interval < 1:
            depth += 1
            interval, equal = p.interval_between(q, depth)

        step = min(self.BOUNDARY, randint(0, interval - 1) + 1)

        if self._strategy.for_depth(depth) or equal:
            res = p.to_int(depth) + step
        else:
            res = q.to_int(depth) - step

        sites = p.sites + [self.site]

        return Position.from_int(res, depth, sites, base_bits=p.base_bits)

    def apply_patch(self, patch: str) -> None:
        json_char = json.loads(patch)
        op = json_char["op"]

        if op == "i":
            char = Char(json_char["char"], Position(json_char["pos"], json_char["sites"]), json_char["clock"])
            self._doc.add(char)
        elif op == "d":
            char = next(c for c in self._doc if
                        c.pos.pos == json_char["pos"] and
                        c.pos.sites == json_char["sites"] and
                        c.clock == json_char["clock"]
                        )
            self._doc.remove(char)

    def _serialize(self, op: str, char: "Char") -> str:
        patch = {"op": op, "src": self.site}
        patch.update({
            "char": char.char,
            "pos": char.pos.pos,
            "sites": char.pos.sites,
            "clock": char.clock
        })
        return json.dumps(patch)

    def debug(self):
        for char in self._doc:
            print(f"<{char.char.encode()}, {char.pos}, L{char.clock}> ", end="")

        print()

    @property
    def text(self) -> str:
        return "".join([c.char for c in self._doc])
