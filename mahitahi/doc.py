import json

from random import randint
from sortedcontainers import SortedList
from typing import Dict, Sequence, List

from .alloc import Allocator
from .char import Char
from .position import Position, BASE_BITS
from .strategy import RandomStrategy


class Doc:

    PATCH_INSERT_TOKEN = "i"
    PATCH_DELETE_TOKEN = "d"

    def __init__(self, site: int=0) -> None:
        self._site: int = site

        self._strategy = RandomStrategy()
        self._alloc = Allocator(self._strategy, self.site)

        self._clock: int = 0
        self._doc: SortedList["Char"] = SortedList()
        self._doc.add(Char("", Position([0], [-1]), self._clock))
        self._doc.add(Char("", Position([2 ** BASE_BITS - 1], [-1]), self._clock))

    def insert(self, pos: int, char: str) -> str:
        self._clock += 1
        p, q = self._doc[pos].pos, self._doc[pos + 1].pos

        new_char = Char(char, self._alloc(p, q), self._clock)
        self._doc.add(new_char)

        return self._serialize(self.PATCH_INSERT_TOKEN, new_char)

    def delete(self, pos: int) -> str:
        self._clock += 1
        old_char = self._doc[pos + 1]
        self._doc.remove(old_char)

        return self._serialize(self.PATCH_DELETE_TOKEN, old_char)

    def apply_patch(self, patch: str) -> None:
        json_char = json.loads(patch)
        op = json_char["op"]

        if op == self.PATCH_INSERT_TOKEN:
            char = Char(json_char["char"], Position(
                json_char["pos"], json_char["sites"]), json_char["clock"])
            self._doc.add(char)
        elif op == self.PATCH_DELETE_TOKEN:
            char = next(c for c in self._doc if
                        c.pos.pos == json_char["pos"] and
                        c.pos.sites == json_char["sites"] and
                        c.clock == json_char["clock"]
                        )
            self._doc.remove(char)

    def _serialize(self, op: str, char: "Char") -> str:
        patch = {
            "op": op,
            "src": self.site,
            "char": char.char,
            "pos": char.pos.pos,
            "sites": char.pos.sites,
            "clock": char.clock
        }
        return json.dumps(patch)

    def debug(self) -> None:
        for char in self._doc:
            print(f"<{char.char.encode()}, {char.pos}, L{char.clock}>\n", end="")

        print()

    @property
    def site(self) -> int:
        return self._site

    @site.setter
    def site(self, value: int) -> None:
        self._site = value
        self._alloc = Allocator(self._strategy, value)

    @property
    def text(self) -> str:
        return "".join([c.char for c in self._doc])

    @property
    def authors(self) -> List[int]:
        return [c.author for c in self._doc]

    @property
    def patch_set(self) -> List[str]:
        return [self._serialize(self.PATCH_INSERT_TOKEN, c) for c in self._doc[1:-1]]
