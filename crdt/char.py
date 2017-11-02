from .position import Position


class Char:

    def __init__(self, char: str, pos: "Position", site: int, clock: int) -> None:
        self.char = char
        self.pos = pos
        self.site = site
        self.clock = clock

    def __lt__(self, other: "Char"):
        # Lexical order by `position` followed by `site` as tie-breaker
        if self.pos < other.pos:
            return True
        elif self.pos == other.pos:
            if self.site < other.site:
                return True
            else:
                return False
