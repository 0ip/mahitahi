class Char:

    def __init__(self, char: str, pos: "Position", clock: int) -> None:
        self.char = char
        self.pos = pos
        self.clock = clock

    @property
    def author(self) -> int:
        return self.pos.sites[-1]

    def __lt__(self, other: "Char"):
        return self.pos < other.pos
