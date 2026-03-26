from dataclasses import dataclass, field
from pieces import Piece
import math
import copy

sign = lambda x: math.copysign(1, x)

@dataclass
class Board:
    structure: list[list[object | None]] = field(
        default_factory=lambda: [[None for _ in range(8)] for _ in range(8)]
    )
    en_passant_target: tuple[int, int] | None = None

    #clears board entirely
    def clear_board(self):
        self.structure = [[None for _ in range(8)] for _ in range(8)]
    
    #resets board to default chess beginning state
    def reset_board(self):
        self.clear_board()

        self.structure[0][0] = Piece(color="Black", kind="Rook")
        self.structure[0][1] = Piece(color="Black", kind="Knight")
        self.structure[0][2] = Piece(color="Black", kind="Bishop")
        self.structure[0][3] = Piece(color="Black", kind="Queen")
        self.structure[0][4] = Piece(color="Black", kind="King")
        self.structure[0][5] = Piece(color="Black", kind="Bishop")
        self.structure[0][6] = Piece(color="Black", kind="Knight")
        self.structure[0][7] = Piece(color="Black", kind="Rook")
        for ii in range(8):
            self.structure[1][ii] = Piece(color="Black")

        self.structure[7][0] = Piece(color="White", kind="Rook")
        self.structure[7][1] = Piece(color="White", kind="Knight")
        self.structure[7][2] = Piece(color="White", kind="Bishop")
        self.structure[7][3] = Piece(color="White", kind="Queen")
        self.structure[7][4] = Piece(color="White", kind="King")
        self.structure[7][5] = Piece(color="White", kind="Bishop")
        self.structure[7][6] = Piece(color="White", kind="Knight")
        self.structure[7][7] = Piece(color="White", kind="Rook")
        for ii in range(8):
            self.structure[6][ii] = Piece(color="White")
    
    #displays the board in the terminal
    def display_board(self):
        header_row = [" ", "a ", "b ", "c ", "d ", "e ", "f ", "g ", "h "]
        print(" ".join(header_row))
        for ii, row in enumerate(self.structure):
            display_row = [str(8-ii)]
            for square in row:
                if square is None:
                    display_row.append("--")
                else:
                    display_row.append(str(square))
            print(" ".join(display_row))
    
    #copies the board state
    def deepcopy(self):
        return copy.deepcopy(self)
    
    #finds all instances of a specific piece on the board
    def find_piece(self, piece, from_rank=None, from_file=None):
        piece_indices = []
        for row_index, row in enumerate(self.structure):
            for column_index, square in enumerate(row):
                if square is not None and square.color == piece.color and square.kind == piece.kind:
                    piece_indices.append([row_index, column_index])
        
        if from_rank is not None:
            piece_indices = [index for index in piece_indices if index[0] == from_rank]
        
        if from_file is not None:
            piece_indices = [index for index in piece_indices if index[1] == from_file]

        return piece_indices
    
    #returns whatever is on the indexed square
    def square_check(self, index1, index2):
        return self.structure[index1][index2]
    
    #finds king of a certain color on the board
    def find_king(self, color):
        for row_index, row in enumerate(self.structure):
            for col_index, square in enumerate(row):
                if square is not None and square.kind == "King" and square.color == color:
                    return [row_index, col_index]

    #finds remainig pieces on the board for each color
    def remaining_pieces(self):
        white = []
        black = []

        for row in self.structure:
            for square in row:
                if square is None:
                    continue
                if square.color == "White":
                    white.append(square)
                else:
                    black.append(square)

        return white, black

    #returns FEN string for piece placement
    def fen_piece_placement(self):
        piece_dict = {
            "Pawn": "P",
            "Knight": "N",
            "Bishop": "B",
            "Rook": "R",
            "Queen": "Q",
            "King": "K"
        }

        fen_rows = []

        for row in self.structure:
            row_fen = ""
            none_counter = 0

            for square in row:
                if square is None:
                    none_counter += 1
                else:
                    if none_counter > 0:
                        row_fen += str(none_counter)
                        none_counter = 0

                    piece_letter = piece_dict[square.kind]
                    if square.color == "Black":
                        piece_letter = piece_letter.lower()

                    row_fen += piece_letter

            if none_counter > 0:
                row_fen += str(none_counter)

            fen_rows.append(row_fen)

        return "/".join(fen_rows)

    #returns FEN string for castling rights
    def castling_rights_string(self):
        castle_string = ""

        white_king = self.square_check(7, 4)
        white_rook_q = self.square_check(7, 0)
        white_rook_k = self.square_check(7, 7)

        black_king = self.square_check(0, 4)
        black_rook_q = self.square_check(0, 0)
        black_rook_k = self.square_check(0, 7)

        if (
            white_king is not None
            and white_king.kind == "King"
            and white_king.color == "White"
            and not white_king.has_moved
            and white_rook_k is not None
            and white_rook_k.kind == "Rook"
            and white_rook_k.color == "White"
            and not white_rook_k.has_moved
        ):
            castle_string += "K"

        if (
            white_king is not None
            and white_king.kind == "King"
            and white_king.color == "White"
            and not white_king.has_moved
            and white_rook_q is not None
            and white_rook_q.kind == "Rook"
            and white_rook_q.color == "White"
            and not white_rook_q.has_moved
        ):
            castle_string += "Q"

        if (
            black_king is not None
            and black_king.kind == "King"
            and black_king.color == "Black"
            and not black_king.has_moved
            and black_rook_k is not None
            and black_rook_k.kind == "Rook"
            and black_rook_k.color == "Black"
            and not black_rook_k.has_moved
        ):
            castle_string += "k"

        if (
            black_king is not None
            and black_king.kind == "King"
            and black_king.color == "Black"
            and not black_king.has_moved
            and black_rook_q is not None
            and black_rook_q.kind == "Rook"
            and black_rook_q.color == "Black"
            and not black_rook_q.has_moved
        ):
            castle_string += "q"

        if castle_string == "":
            return "-"

        return castle_string

    #returns FEN string for en passant square
    def en_passant_fen_square(self):
        if self.en_passant_target is None:
            return "-"

        row, col = self.en_passant_target
        file_letter = chr(ord("a") + col)
        rank_number = str(8 - row)

        return file_letter + rank_number
            
    #helps with rook/bishop/queen scanning logic for is_attacked, similar to moves_in_direction
    def is_attacked_helper(self, victim_color, row, col, d_row, d_col):
        current_row = row + d_row
        current_col = col + d_col

        while 0 <= current_row <= 7 and 0 <= current_col <= 7:
            square = self.square_check(current_row, current_col)

            if square is None:
                current_row += d_row
                current_col += d_col
                continue

            if square.color != victim_color:
                return [current_row, current_col]
            
            return None

        return None
    
    #determined if a given square at row, col is under attack by pieces with color opposite to victim_color
    def is_attacked(self, row, col, victim_color):
        straight_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        diagonal_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for d_row, d_col in straight_directions:
            square_index = self.is_attacked_helper(victim_color, row, col, d_row, d_col)
            if square_index is not None:
                s_row, s_col = square_index
                piece = self.square_check(s_row, s_col)
                if piece.kind in ("Queen", "Rook"):
                    return True

        for d_row, d_col in diagonal_directions:
            square_index = self.is_attacked_helper(victim_color, row, col, d_row, d_col)
            if square_index is not None:
                s_row, s_col = square_index
                piece = self.square_check(s_row, s_col)
                if piece.kind in ("Queen", "Bishop"):
                    return True
        
        knight_checklist = [
                [row + 1, col + 2], [row + 2, col + 1],
                [row - 1, col + 2], [row - 2, col + 1],
                [row + 1, col - 2], [row + 2, col - 1],
                [row - 1, col - 2], [row - 2, col - 1]
            ]

        for square in knight_checklist:
            s_row, s_col = square
            if not (0 <= s_row <= 7 and 0 <= s_col <= 7):
                continue

            target = self.square_check(s_row, s_col)
            if target is not None and target.kind == "Knight" and target.color != victim_color:
                return True
        
        king_checklist = [
                [row + 1, col + 1], [row + 1, col], [row + 1, col - 1],
                [row, col + 1], [row, col - 1],
                [row - 1, col + 1], [row - 1, col], [row - 1, col - 1]
            ]

        for square in king_checklist:
            s_row, s_col = square
            if not (0 <= s_row <= 7 and 0 <= s_col <= 7):
                continue

            target = self.square_check(s_row, s_col)
            if target is not None and target.kind == "King" and target.color != victim_color:
                return True
        
        if victim_color == "Black":
            if 0 <= row + 1 <= 7:
                if 0 <= col + 1 <= 7:
                    target = self.square_check(row + 1, col + 1)
                    if target is not None and target.kind == "Pawn" and target.color != victim_color:
                        return True

                if 0 <= col - 1 <= 7:
                    target = self.square_check(row + 1, col - 1)
                    if target is not None and target.kind == "Pawn" and target.color != victim_color:
                        return True
        
        elif victim_color == "White":
            if 0 <= row - 1 <= 7:
                if 0 <= col + 1 <= 7:
                    target = self.square_check(row - 1, col + 1)
                    if target is not None and target.kind == "Pawn" and target.color != victim_color:
                        return True

                if 0 <= col - 1 <= 7:
                    target = self.square_check(row - 1, col - 1)
                    if target is not None and target.kind == "Pawn" and target.color != victim_color:
                        return True


        return False
    
    #checks if a color has any legal moves
    def has_any_legal_move(self, color):
        for row_index, row in enumerate(self.structure):
            for col_index, square in enumerate(row):
                if square is None:
                    continue

                if square.color != color:
                    continue

                legal_moves = self.legal_moves_preking(square, row_index, col_index)

                for move in legal_moves:
                    temp_board = self.deepcopy()
                    temp_board.make_move(row_index, col_index, move)

                    king_row, king_col = temp_board.find_king(color)
                    if not temp_board.is_attacked(king_row, king_col, color):
                        return True

        return False

    #gives a list of dictionaries with all legal moves for a color in a position (includes piece kind and color)
    def all_legal_moves(self, color):
        all_moves = []

        for row_index, row in enumerate(self.structure):
            for col_index, square in enumerate(row):
                if square is None:
                    continue

                if square.color != color:
                    continue

                candidate_moves = self.legal_moves_preking(square, row_index, col_index)

                for move in candidate_moves:
                    temp_board = self.deepcopy()
                    temp_board.make_move(row_index, col_index, move)

                    king_row, king_col = temp_board.find_king(color)
                    if not temp_board.is_attacked(king_row, king_col, color):
                        all_moves.append({
                            "piece": square.kind,
                            "color": square.color,
                            "start": (row_index, col_index),
                            "end": tuple(move)
                        })

        return all_moves
    
    #scans for checks on victim color
    def is_check(self, victim_color):
        k_row, k_col = self.find_king(victim_color)
        return self.is_attacked(k_row, k_col, victim_color)
    
    #scans for checkmate on victim color
    def is_checkmate(self, victim_color):
        if self.is_check(victim_color) and not self.has_any_legal_move(victim_color):
            return True
        else:
            return False
    
    #scans for stalemate on victim color
    def is_stalemate(self, victim_color):
        if not self.is_check(victim_color) and not self.has_any_legal_move(victim_color):
            return True
        else:
            return False
    
    #promotes a pawn to selected piece
    def promote_pawn(self, row, col, new_kind):
        piece = self.square_check(row, col)
        if piece is None or piece.kind != "Pawn":
            return

        values = {
            "Queen": 9,
            "Rook": 5,
            "Bishop": 3,
            "Knight": 3
        }

        if new_kind not in values:
            return

        self.structure[row][col] = Piece(
            color=piece.color,
            kind=new_kind,
            value=values[new_kind],
            is_captured=False,
            has_moved=True
        )
    
    #moves a piece from one place to another and both captures and notes captured pieces // also handles calling for promotion
    def make_move(self, row, col, move, promotion="Queen"):
        target_is_none = False
        old_en_passant_target = self.en_passant_target
        self.en_passant_target = None
        is_castle = False
        row_m, col_m = move
        piece = self.square_check(row, col)
        captured_piece = None
        piece_had_moved = piece.has_moved
        is_promotion = False

        if piece is None:
            return None

        if self.structure[row_m][col_m] is not None:
            captured_piece = self.structure[row_m][col_m]
            captured_piece.is_captured = True
        else:
            target_is_none = True

        self.structure[row][col] = None
        self.structure[row_m][col_m] = piece
        piece.has_moved = True

        # castling logic
        if piece.kind == "King" and abs(col_m - col) == 2:
            is_castle = True
            if row_m == 0 and col_m == 2:
                rook = self.square_check(0, 0)
                self.structure[0][0] = None
                self.structure[0][3] = rook
                rook.has_moved = True

            elif row_m == 0 and col_m == 6:
                rook = self.square_check(0, 7)
                self.structure[0][7] = None
                self.structure[0][5] = rook
                rook.has_moved = True

            elif row_m == 7 and col_m == 2:
                rook = self.square_check(7, 0)
                self.structure[7][0] = None
                self.structure[7][3] = rook
                rook.has_moved = True

            elif row_m == 7 and col_m == 6:
                rook = self.square_check(7, 7)
                self.structure[7][7] = None
                self.structure[7][5] = rook
                rook.has_moved = True

        #en passant target setup
        if piece.kind == "Pawn" and abs(row_m - row) == 2:
            if piece.color == "Black":
                self.en_passant_target = (row + 1, col)
            else:
                self.en_passant_target = (row - 1, col)

        #en passant capture
        if piece.kind == "Pawn" and abs(col_m - col) == 1 and target_is_none:
            if old_en_passant_target == (row_m, col_m):
                if piece.color == "White":
                    captured_piece = self.square_check(row_m + 1, col_m)
                    captured_piece.is_captured = True
                    self.structure[row_m + 1][col_m] = None
                else:
                    captured_piece = self.square_check(row_m - 1, col_m)
                    captured_piece.is_captured = True
                    self.structure[row_m - 1][col_m] = None

        #promotion
        if piece.kind == "Pawn":
            if piece.color == "Black" and row_m == 7:
                is_promotion = True
                self.promote_pawn(row_m, col_m, promotion)
            elif piece.color == "White" and row_m == 0:
                is_promotion = True
                self.promote_pawn(row_m, col_m, promotion)

        return {
            "piece": piece.kind,
            "color": piece.color,
            "start": (row, col),
            "end": (row_m, col_m),
            "capture": captured_piece is not None,
            "captured_piece": captured_piece,
            "is_castle": is_castle,
            "piece_had_moved": piece_had_moved,
            "en_passant_target_at_move": old_en_passant_target,
            "is_promotion": is_promotion,
            "promotion_piece": promotion if is_promotion else None
        }

    #a checker that scans outward from a square in steps of d_row, d_col for pieces to determine move legality
    def moves_in_direction(self, row, col, d_row, d_col):
        piece = self.square_check(row, col)
        legal_moves = []

        current_row = row + d_row
        current_col = col + d_col

        #sliding piece logic
        while 0 <= current_row <= 7 and 0 <= current_col <= 7:
            square = self.square_check(current_row, current_col)

            if square is None:
                legal_moves.append([current_row, current_col])

            elif square.color != piece.color:
                legal_moves.append([current_row, current_col])
                break

            else:
                break

            current_row += d_row
            current_col += d_col

        return legal_moves
    
    #checks if castling queenside is legitimate for a king/rook pair of one color
    def can_castle_queenside(self, king, rook):
        if rook is None:
            return False
        if king.has_moved == False and rook.has_moved == False:
            if king.color == "White":
                if self.square_check(7, 3) is None and self.square_check(7, 2) is None and self.square_check(7, 1) is None:
                    if self.is_attacked(7, 4, "White") == False and self.is_attacked(7, 3, "White") == False and self.is_attacked(7, 2, "White") == False:
                        return True
            if king.color == "Black":
                if self.square_check(0, 3) is None and self.square_check(0, 2) is None and self.square_check(0, 1) is None:
                    if self.is_attacked(0, 4, "Black") == False and self.is_attacked(0, 3, "Black") == False and self.is_attacked(0, 2, "Black") == False:
                        return True
        else:
            return False

    #checks if castling kingside is legitimate for a king/rook pair of one color
    def can_castle_kingside(self, king, rook):
        if rook is None:
            return False
        if king.has_moved == False and rook.has_moved == False:
            if king.color == "White":
                if self.square_check(7, 5) is None and self.square_check(7, 6) is None:
                    if self.is_attacked(7, 4, "White") == False and self.is_attacked(7, 5, "White") == False and self.is_attacked(7, 6, "White") == False:
                        return True
            if king.color == "Black":
                if self.square_check(0, 5) is None and self.square_check(0, 6) is None:
                    if self.is_attacked(0, 4, "Black") == False and self.is_attacked(0, 5, "Black") == False and self.is_attacked(0, 6, "Black") == False:
                        return True
        else:
            return False
        
    #generate a list of all legal moves from a selected piece at some position excluding king safety requirements
    def legal_moves_preking(self, piece, row, col):
        legal_moves = []

        if piece.kind == "Queen":
            legal_moves.extend(self.moves_in_direction(row, col, 1, 0))
            legal_moves.extend(self.moves_in_direction(row, col, 0, 1))
            legal_moves.extend(self.moves_in_direction(row, col, -1, 0))
            legal_moves.extend(self.moves_in_direction(row, col, 0, -1))
            legal_moves.extend(self.moves_in_direction(row, col, 1, 1))
            legal_moves.extend(self.moves_in_direction(row, col, 1, -1))
            legal_moves.extend(self.moves_in_direction(row, col, -1, 1))
            legal_moves.extend(self.moves_in_direction(row, col, -1, -1))

        elif piece.kind == "Rook":
            legal_moves.extend(self.moves_in_direction(row, col, 1, 0))
            legal_moves.extend(self.moves_in_direction(row, col, 0, 1))
            legal_moves.extend(self.moves_in_direction(row, col, -1, 0))
            legal_moves.extend(self.moves_in_direction(row, col, 0, -1))

        elif piece.kind == "Bishop":
            legal_moves.extend(self.moves_in_direction(row, col, 1, 1))
            legal_moves.extend(self.moves_in_direction(row, col, 1, -1))
            legal_moves.extend(self.moves_in_direction(row, col, -1, 1))
            legal_moves.extend(self.moves_in_direction(row, col, -1, -1))

        elif piece.kind == "Knight":
            knight_checklist = [
                [row + 1, col + 2], [row + 2, col + 1],
                [row - 1, col + 2], [row - 2, col + 1],
                [row + 1, col - 2], [row + 2, col - 1],
                [row - 1, col - 2], [row - 2, col - 1]
            ]

            for square in knight_checklist:
                s_row, s_col = square
                if not (0 <= s_row <= 7 and 0 <= s_col <= 7):
                    continue

                target = self.square_check(s_row, s_col)
                if target is None or target.color != piece.color:
                    legal_moves.append(square)

        elif piece.kind == "King":
            king_checklist = [
                [row + 1, col + 1], [row + 1, col], [row + 1, col - 1],
                [row, col + 1], [row, col - 1],
                [row - 1, col + 1], [row - 1, col], [row - 1, col - 1]
            ]

            for square in king_checklist:
                s_row, s_col = square
                if not (0 <= s_row <= 7 and 0 <= s_col <= 7):
                    continue

                target = self.square_check(s_row, s_col)
                if target is None or target.color != piece.color:
                    legal_moves.append(square)
            
            if piece.color == "Black":
                black_rook_Qcandidate = self.square_check(0, 0)
                black_rook_Kcandidate = self.square_check(0, 7)

                if self.can_castle_queenside(piece, black_rook_Qcandidate):
                    legal_moves.append([0, 2])
                if self.can_castle_kingside(piece, black_rook_Kcandidate):
                    legal_moves.append([0, 6])

            elif piece.color == "White":
                white_rook_Qcandidate = self.square_check(7, 0)
                white_rook_Kcandidate = self.square_check(7, 7)

                if self.can_castle_queenside(piece, white_rook_Qcandidate):
                    legal_moves.append([7, 2])
                if self.can_castle_kingside(piece, white_rook_Kcandidate):
                    legal_moves.append([7, 6])
        
        elif piece.kind == "Pawn":
            if piece.color == "Black":
                if 0 <= row + 1 <= 7:
                    if self.square_check(row + 1, col) is None:
                        legal_moves.append([row + 1, col])

                        if row == 1 and self.square_check(row + 2, col) is None:
                            legal_moves.append([row + 2, col])

                    if 0 <= col + 1 <= 7:
                        target = self.square_check(row + 1, col + 1)
                        if target is not None and target.color != piece.color:
                            legal_moves.append([row + 1, col + 1])
                        if self.en_passant_target is not None and (row + 1, col + 1) == self.en_passant_target:
                            legal_moves.append([row + 1, col + 1])

                    if 0 <= col - 1 <= 7:
                        target = self.square_check(row + 1, col - 1)
                        if target is not None and target.color != piece.color:
                            legal_moves.append([row + 1, col - 1])
                        if self.en_passant_target is not None and (row + 1, col - 1) == self.en_passant_target:
                            legal_moves.append([row + 1, col - 1])
                    

            else:
                if 0 <= row - 1 <= 7:
                    if self.square_check(row - 1, col) is None:
                        legal_moves.append([row - 1, col])

                        if row == 6 and self.square_check(row - 2, col) is None:
                            legal_moves.append([row - 2, col])

                    if 0 <= col + 1 <= 7:
                        target = self.square_check(row - 1, col + 1)
                        if target is not None and target.color != piece.color:
                            legal_moves.append([row - 1, col + 1])
                        if self.en_passant_target is not None and (row - 1, col + 1) == self.en_passant_target:
                            legal_moves.append([row - 1, col + 1])

                    if 0 <= col - 1 <= 7:
                        target = self.square_check(row - 1, col - 1)
                        if target is not None and target.color != piece.color:
                            legal_moves.append([row - 1, col - 1])
                        if self.en_passant_target is not None and (row - 1, col - 1) == self.en_passant_target:
                            legal_moves.append([row - 1, col - 1])
        
        return legal_moves

    #determine the possible starting positions for a piece making a move to some square inputted by the player    
    def moving_piece_start_pos(self, piece, move, from_rank=None, from_file=None):
        possible_piece_locations = self.find_piece(piece)
        possible_starting_squares = []

        for piece_location in possible_piece_locations:
            row, col = piece_location
            board_piece = self.square_check(row, col)
            legal_moves = self.legal_moves_preking(board_piece, row, col)

            if move in legal_moves:
                possible_starting_squares.append(piece_location)

        if from_rank is not None:
            possible_starting_squares = [
                square for square in possible_starting_squares if square[0] == from_rank
            ]

        if from_file is not None:
            possible_starting_squares = [
                square for square in possible_starting_squares if square[1] == from_file
            ]

        return possible_starting_squares

    #checks the generated legal moves for king safety requirements, then narrows potential starting squares if needed    
    def king_check(self, piece, move, promotion="Queen"):
        starting_squares = self.moving_piece_start_pos(piece, move)
        possible_start = []
        for starting_square in starting_squares:
            row, col = starting_square
            board_piece = self.square_check(row, col)
            legal_moves = self.legal_moves_preking(board_piece, row, col)
            
            fully_legal = []
            for candidate_move in legal_moves:
                temp_board = self.deepcopy()
                temp_board.make_move(row, col, candidate_move, promotion)
                
                if temp_board.find_king(board_piece.color) is None:
                    fully_legal.append(candidate_move)
                    continue
                else:
                    king_row, king_col = temp_board.find_king(piece.color)
                    king_color = board_piece.color

                if not temp_board.is_attacked(king_row, king_col, king_color):
                    fully_legal.append(candidate_move)
            
            if move in fully_legal:
                possible_start.append(starting_square)
        return possible_start

    #determines the starting square of the piece to be moved with a final ask to the user if ambiguity remains   
    def is_legal(self, piece, move, from_rank=None, from_file=None):
        starting_squares = self.king_check(piece, move)

        if from_rank is not None:
            starting_squares = [
                square for square in starting_squares if square[0] == from_rank
            ]

        if from_file is not None:
            starting_squares = [
                square for square in starting_squares if square[1] == from_file
            ]

        if len(starting_squares) > 1:
            print(f"Possible starting squares: {starting_squares}")
            raw_indices = input(
                "Please input the indices of the piece you intend to move (separated by a comma): "
            )
            starting_square = [int(x) for x in raw_indices.split(",")]

            while starting_square not in starting_squares:
                print("No valid moves can be made from that square.")
                raw_indices = input(
                "Please input the indices of the piece you intend to move (separated by a comma): "
            )
                starting_square = [int(x) for x in raw_indices.split(",")]

        elif len(starting_squares) == 0:
            return None

        else:
            starting_square = starting_squares[0]

        return starting_square
    
    #call to make a legal move using any piece and some move [row, col]
    def legal_move(self, piece, move, promotion="Queen", from_rank=None, from_file=None):
        moving_piece_index = self.is_legal(piece, move, from_rank, from_file)
        if moving_piece_index is None:
            print("Invalid move, please try again.")
            return None
        
        row, col = moving_piece_index
        move_info = self.make_move(row, col, move, promotion)
        return move_info
