# third party
from chess import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN
import chess

# project
from src.move_ordering.base import MoveSorter

class MvvLva(MoveSorter):
    """
    Reference: https://rustic-chess.org/search/ordering/mvv_lva.html
    """

    # MVV_LVA[victim][attacker] = move_score
    # capturing a queen with a pawn has the highest score
    # capturing nothing has the lowest score
    MVV_LVA = {
        KING:   {KING:  0, QUEEN:  0, ROOK:  0, BISHOP:  0, KNIGHT:  0, PAWN:  0, None: 0},
        QUEEN:  {KING: 50, QUEEN: 51, ROOK: 52, BISHOP: 53, KNIGHT: 54, PAWN: 55, None: 0},
        ROOK:   {KING: 40, QUEEN: 41, ROOK: 42, BISHOP: 43, KNIGHT: 44, PAWN: 45, None: 0},
        BISHOP: {KING: 30, QUEEN: 31, ROOK: 32, BISHOP: 33, KNIGHT: 34, PAWN: 35, None: 0},
        KNIGHT: {KING: 20, QUEEN: 21, ROOK: 22, BISHOP: 23, KNIGHT: 24, PAWN: 25, None: 0},
        PAWN:   {KING: 10, QUEEN: 11, ROOK: 12, BISHOP: 13, KNIGHT: 14, PAWN: 15, None: 0},
        None:   {KING:  0, QUEEN:  0, ROOK:  0, BISHOP:  0, KNIGHT:  0, PAWN:  0, None: 0},
    }

    def sort(self, board: chess.Board, legal_moves: list[chess.Move]) -> list[chess.Move]:
        def score_move(move: chess.Move) -> int:
            if not board.is_capture(move):
                if board.gives_check(move):
                    return 39
                return 0
            
            attacker = board.piece_type_at(move.from_square)
            victim = board.piece_type_at(move.to_square)

            if board.is_en_passant(move):
                victim = PAWN
            
            # score each move based on the MVV_LVA heuristic
            return self.MVV_LVA[victim][attacker]

        # reverse=True ensures that higher scoring moves are at the front
        return sorted(legal_moves, key=score_move, reverse=True)