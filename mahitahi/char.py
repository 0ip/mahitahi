class Char:

    def __init__(self, char: str, pos: "Position", clock: int) -> None:
        self.char = char
        self.pos = pos
        self.clock = clock

    def __lt__(self, other: "Char"):
        return self.pos < other.pos
