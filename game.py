from dataclasses import dataclass, field
from pieces import Piece
from board import Board

@dataclass(frozen=True)
class MoveRecord:
    piece: str
    color: str
    start: tuple[int, int]
    end: tuple[int, int]
    notation: str
    capture: bool = False
    captured_piece: Piece | None = None
    is_castle: bool = False
    piece_had_moved: bool = False
    en_passant_target_at_move: tuple[int, int] | None = None
    is_promotion: bool = False
    promotion_piece: str | None = None

@dataclass
class Game:
    turn: str = "White"
    move_input: str = ""
    board: Board = field(default_factory=Board)
    checkmate: bool = False
    stalemate: bool = False
    move_history: list = field(default_factory=list)
    halfmove_clock: int = 0
    

    def fen_fields(self):
        piece_placement = self.board.fen_piece_placement()
        turn = "w" if self.turn == "White" else "b"
        castling_rights = self.board.castling_rights_string()
        en_passant = self.board.en_passant_fen_square()
        halfmove = str(self.halfmove_clock)
        fullmove = str(len(self.move_history) // 2 + 1)

        return (
            piece_placement,
            turn,
            castling_rights,
            en_passant,
            halfmove,
            fullmove
        )

    def prompt_move(self):
        if self.turn == "White":
            self.move_input = input("White to move: ")
        else:
            self.move_input = input("Black to move: ")

    
    def input_parser(self, move_text):
        move_text = move_text.strip()
        self.move_input = move_text
        if not move_text:
            return None

        file_map = {
            "a": 0, "b": 1, "c": 2, "d": 3,
            "e": 4, "f": 5, "g": 6, "h": 7
        }

        piece_map = {
            "N": "Knight",
            "B": "Bishop",
            "R": "Rook",
            "Q": "Queen",
            "K": "King"
        }

        result = {
            "piece": None,
            "move": None,
            "capture": False,
            "from_file": None,
            "from_rank": None,
            "promotion": None,
            "castle": None,
        }

        lower_text = move_text.lower()

        # castling
        if lower_text == "o-o":
            k_row, k_col = self.board.find_king(self.turn)
            king = self.board.square_check(k_row, k_col)
            result["piece"] = king
            result["move"] = [k_row, k_col + 2]
            result["castle"] = "kingside"
            return result

        if lower_text == "o-o-o":
            k_row, k_col = self.board.find_king(self.turn)
            king = self.board.square_check(k_row, k_col)
            result["piece"] = king
            result["move"] = [k_row, k_col - 2]
            result["castle"] = "queenside"
            return result

        # strip trailing + or #
        while move_text and move_text[-1] in ("+", "#"):
            move_text = move_text[:-1]

        if not move_text:
            return None

        # promotion
        if "=" in move_text:
            move_text, promo_part = move_text.split("=")
            promo_part = promo_part.strip()
            promo_map = {
                "Q": "Queen",
                "R": "Rook",
                "B": "Bishop",
                "N": "Knight"
            }
            if promo_part not in promo_map:
                return None
            result["promotion"] = promo_map[promo_part]

        # capture
        if "x" in move_text:
            result["capture"] = True
            move_text = move_text.replace("x", "")

        if not move_text:
            return None

        # helper to convert file/rank to board indices
        def square_to_indices(file_char, rank_char):
            if file_char not in file_map:
                return None
            if not rank_char.isdigit():
                return None

            row = 8 - int(rank_char)
            col = file_map[file_char]

            if not (0 <= row <= 7):
                return None

            return [row, col]

        # piece move
        if move_text[0] in piece_map:
            result["piece"] = Piece(color=self.turn, kind=piece_map[move_text[0]])
            body = move_text[1:]

            # supported piece forms after stripping x:
            # f3       -> body length 2
            # bd2      -> body length 3, from file
            # 1e2      -> body length 3, from rank
            # e4d5     -> body length 4, full origin square
            if len(body) == 2:
                target = square_to_indices(body[0], body[1])
                if target is None:
                    return None
                result["move"] = target
                return result

            elif len(body) == 3:
                disamb = body[0]
                target = square_to_indices(body[1], body[2])
                if target is None:
                    return None

                if disamb in file_map:
                    result["from_file"] = file_map[disamb]
                elif disamb.isdigit():
                    disamb_row = 8 - int(disamb)
                    if not (0 <= disamb_row <= 7):
                        return None
                    result["from_rank"] = disamb_row
                else:
                    return None

                result["move"] = target
                return result

            elif len(body) == 4:
                # full origin square + target square
                origin = square_to_indices(body[0], body[1])
                target = square_to_indices(body[2], body[3])
                if origin is None or target is None:
                    return None

                result["from_file"] = origin[1]
                result["from_rank"] = origin[0]
                result["move"] = target
                return result

            else:
                return None

        # pawn move
        else:
            result["piece"] = Piece(color=self.turn, kind="Pawn")
            body = move_text

            # supported pawn forms after stripping x:
            # e4       -> len 2
            # ed5      -> len 3, capture with origin file
            # e4e5     -> len 4, full origin square + target square
            # e4d5     -> len 4, full origin square + target square capture-style after x removed
            if len(body) == 2:
                target = square_to_indices(body[0], body[1])
                if target is None:
                    return None
                result["move"] = target
                return result

            elif len(body) == 3:
                # exd5 becomes ed5 after removing x
                if body[0] not in file_map:
                    return None
                target = square_to_indices(body[1], body[2])
                if target is None:
                    return None

                result["from_file"] = file_map[body[0]]
                result["move"] = target
                return result

            elif len(body) == 4:
                origin = square_to_indices(body[0], body[1])
                target = square_to_indices(body[2], body[3])
                if origin is None or target is None:
                    return None

                result["from_file"] = origin[1]
                result["from_rank"] = origin[0]
                result["move"] = target
                return result

            else:
                return None

    def begin_game(self):
        self.board.reset_board()
        self.board.display_board()


    def play_turn(self):
        while True:
            self.prompt_move()
            parsed = self.input_parser(self.move_input)
            if parsed is None:
                print("Invalid notation, please try again.")
                continue

            piece = parsed["piece"]
            move = parsed["move"]
            promotion = parsed["promotion"]
            from_rank = parsed["from_rank"]
            from_file = parsed["from_file"]

            move_info = self.board.legal_move(piece, move, promotion, from_rank, from_file)
            
            if move_info is None:
                continue
            

            record = MoveRecord(
                notation = self.move_input,
                **move_info
            )
            self.move_history.append(record)
    
            if self.turn == "White":
                self.turn = "Black"
            else:
                self.turn = "White"

            self.board.display_board()

            if record.piece == "Pawn" or record.capture:
                self.halfmove_clock = 0
            else:
                self.halfmove_clock += 1
            
            if self.halfmove_clock >= 100:
                print("50 move rule reached.")
                self.stalemate = True
            
            white_pieces, black_pieces = self.board.remaining_pieces()
            white_pieces = sorted(white_pieces)
            black_pieces = sorted(black_pieces)

            draw_conditions = [
                (["King"], ["King"]),
                (["Bishop", "King"], ["King"]),
                (["King"], ["Bishop", "King"]),
                (["King", "Knight"], ["King"]),
                (["King"], ["King", "Knight"]),
            ]

            if (white_pieces, black_pieces) in draw_conditions:
                print("Insufficient material.")
                self.stalemate = True

            if not self.stalemate:
                self.stalemate = self.board.is_stalemate(self.turn)
            if self.board.is_check(self.turn):
                self.checkmate = self.board.is_checkmate(self.turn)
            return
        
    def play_game(self):
        while not self.checkmate and not self.stalemate:
            self.play_turn()
        if self.stalemate:
            print("Game is over, it is a stalemate!")
        if self.checkmate:
            if self.turn == "White":
                self.turn = "Black"
            else:
                self.turn = "White"
            print(f"The position is checkmate, {self.turn} wins!")
            for i, move in enumerate(self.move_history, start=1):
                print(f"{i}. {move.color}: {move.notation}")
