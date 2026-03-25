from board import Board
from pieces import Piece


def piece_at(board, row, col):
    return board.square_check(row, col)


def test_white_kingside_castling_works():
    b = Board()
    b.reset_board()

    assert b.legal_move(Piece("White"), [4, 4]) is True               # e4
    assert b.legal_move(Piece("White", "Bishop", 3), [6, 4]) is True  # Be2
    assert b.legal_move(Piece("White", "Knight", 3), [5, 5]) is True  # Nf3
    assert b.legal_move(Piece("White", "King"), [7, 6]) is True       # O-O by coords

    assert piece_at(b, 7, 6) is not None
    assert piece_at(b, 7, 6).kind == "King"
    assert piece_at(b, 7, 6).color == "White"

    assert piece_at(b, 7, 5) is not None
    assert piece_at(b, 7, 5).kind == "Rook"
    assert piece_at(b, 7, 5).color == "White"

    assert piece_at(b, 7, 4) is None
    assert piece_at(b, 7, 7) is None


def test_white_kingside_castling_fails_after_king_moved():
    b = Board()
    b.reset_board()

    assert b.legal_move(Piece("White"), [5, 4]) is True                # e3
    assert b.legal_move(Piece("White", "Bishop", 3), [5, 3]) is True   # Bd3-ish path clear
    assert b.legal_move(Piece("White", "Knight", 3), [5, 5]) is True   # Nf3

    assert b.legal_move(Piece("White", "King"), [6, 4]) is True        # Ke2
    assert b.legal_move(Piece("White", "King"), [7, 4]) is True        # Ke1 back
    assert b.legal_move(Piece("White", "King"), [7, 6]) is False       # try castle

    assert piece_at(b, 7, 4) is not None
    assert piece_at(b, 7, 4).kind == "King"
    assert piece_at(b, 7, 6) is None


def test_white_kingside_castling_fails_through_attacked_square():
    b = Board()
    b.reset_board()

    assert b.legal_move(Piece("White"), [4, 4]) is True                # e4
    assert b.legal_move(Piece("White", "Bishop", 3), [6, 4]) is True   # Be2
    assert b.legal_move(Piece("White", "Knight", 3), [5, 5]) is True   # Nf3
    assert b.legal_move(Piece("White", "Knight", 3), [4, 7]) is True
    assert b.legal_move(Piece("White"), [5, 5]) is True

    assert b.legal_move(Piece("Black"), [3, 4]) is True                # ...e5
    assert b.legal_move(Piece("Black", "Bishop", 3), [3, 2]) is True   # bishop attacks route

    assert b.legal_move(Piece("White", "King"), [7, 6]) is False       # try castle

    assert piece_at(b, 7, 4) is not None
    assert piece_at(b, 7, 4).kind == "King"
    assert piece_at(b, 7, 6) is None


def test_white_en_passant_works():
    b = Board()
    b.reset_board()

    assert b.legal_move(Piece("White"), [4, 4]) is True   # e4
    assert b.legal_move(Piece("White"), [3, 4]) is True   # e5
    assert b.legal_move(Piece("Black"), [3, 3]) is True   # d5 double step

    assert b.en_passant_target == (2, 3)

    assert b.legal_move(Piece("White"), [2, 3]) is True   # exd6 en passant

    assert piece_at(b, 2, 3) is not None
    assert piece_at(b, 2, 3).kind == "Pawn"
    assert piece_at(b, 2, 3).color == "White"

    assert piece_at(b, 3, 3) is None


def test_en_passant_expires():
    b = Board()
    b.reset_board()

    assert b.legal_move(Piece("White"), [4, 4]) is True                # e4
    assert b.legal_move(Piece("White"), [3, 4]) is True                # e5
    assert b.legal_move(Piece("Black"), [3, 3]) is True                # d5

    assert b.en_passant_target == (2, 3)

    assert b.legal_move(Piece("White", "Knight", 3), [5, 5]) is True   # do something else first

    assert b.en_passant_target is None
    assert b.legal_move(Piece("White"), [2, 3]) is False               # en passant should now fail


def test_white_promotion_works():
    b = Board()
    b.clear_board()

    b.structure[1][0] = Piece("White")   # white pawn on a7
    assert b.legal_move(Piece("White"), [0, 0], promotion="Queen") is True

    assert piece_at(b, 0, 0) is not None
    assert piece_at(b, 0, 0).kind == "Queen"
    assert piece_at(b, 0, 0).color == "White"


def test_promotion_defaults_to_queen():
    b = Board()
    b.clear_board()

    b.structure[1][1] = Piece("White")
    assert b.legal_move(Piece("White"), [0, 1]) is True

    assert piece_at(b, 0, 1) is not None
    assert piece_at(b, 0, 1).kind == "Queen"
    assert piece_at(b, 0, 1).color == "White"


def test_pinned_piece_cannot_move():
    b = Board()
    b.clear_board()

    b.structure[7][4] = Piece("White", "King")
    b.structure[6][4] = Piece("White", "Rook", 5)
    b.structure[0][4] = Piece("Black", "Rook", 5)

    assert b.legal_move(Piece("White", "Rook", 5), [6, 5]) is False

    assert piece_at(b, 6, 4) is not None
    assert piece_at(b, 6, 4).kind == "Rook"
    assert piece_at(b, 6, 5) is None


def test_king_cannot_move_into_check():
    b = Board()
    b.clear_board()

    b.structure[7][3] = Piece("White", "King")
    b.structure[5][4] = Piece("Black", "Rook", 5)

    assert b.legal_move(Piece("White", "King"), [7, 4]) is False

    assert piece_at(b, 7, 3) is not None
    assert piece_at(b, 7, 3).kind == "King"
    assert piece_at(b, 7, 4) is None


def test_move_out_of_check_works():
    b = Board()
    b.clear_board()

    b.structure[7][4] = Piece("White", "King")
    b.structure[5][4] = Piece("Black", "Rook", 5)

    assert b.legal_move(Piece("White", "King"), [7, 3]) is True

    assert piece_at(b, 7, 3) is not None
    assert piece_at(b, 7, 3).kind == "King"
    assert piece_at(b, 7, 4) is None


if __name__ == "__main__":
    test_white_kingside_castling_works()
    test_white_kingside_castling_fails_after_king_moved()
    test_white_kingside_castling_fails_through_attacked_square()
    test_white_en_passant_works()
    test_en_passant_expires()
    test_white_promotion_works()
    test_promotion_defaults_to_queen()
    test_pinned_piece_cannot_move()
    test_king_cannot_move_into_check()
    test_move_out_of_check_works()
    print("All tests passed.")