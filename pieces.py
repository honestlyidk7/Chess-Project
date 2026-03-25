from dataclasses import dataclass, field

@dataclass
class Piece:
    color: str = "White"
    kind: str = "Pawn"
    value: int = field(init=False)
    is_captured: bool = False
    has_moved: bool = False

    def __post_init__(self):
        piece_values = {
            "Pawn": 1,
            "Knight": 3,
            "Bishop": 3,
            "Rook": 5,
            "Queen": 9,
            "King": 0
        }

        if self.kind not in piece_values:
            raise ValueError(
                f"Invalid piece kind: {self.kind}. "
                f"Expected one of {list(piece_values.keys())}"
            )

        if self.color not in ("White", "Black"):
            raise ValueError(
                f"Invalid piece color: {self.color}. Expected 'White' or 'Black'"
            )

        self.value = piece_values[self.kind]

    def __repr__(self):
        if self.kind != "Knight":
            return f"{self.color[0]}{self.kind[0]}"
        return f"{self.color[0]}N"

