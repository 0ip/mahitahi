from random import randint

from .position import Position

BOUNDARY = 5


class Allocator:

    def __init__(self, strategy: "Strategy", site: int) -> None:
        self._strategy = strategy
        self._site = site

    def alloc(self, p: "Position", q: "Position") -> "Position":
        if p.pos == q.pos and p.sites == q.sites:
            raise Exception("Cannot allocate between identical identifiers.")

        depth = 0
        interval = 0
        equal = False
        while interval < 1:
            depth += 1
            interval, equal = p.interval_between(q, depth)

        step = min(BOUNDARY, randint(0, interval - 1) + 1)

        if self._strategy.for_depth(depth) or equal:
            res = p.to_int(depth) + step
        else:
            res = q.to_int(depth) - step

        sites_len = depth - len(p.sites)
        sites = p.sites + [self._site] * sites_len
        sites[-1] = self._site

        return Position.from_int(res, depth, sites, base_bits=p.base_bits)

    def __call__(self, p: "Position", q: "Position") -> "Position":
        return self.alloc(p, q)
