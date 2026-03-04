# third party
from chess import KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN
import chess

class MoveOrdering:
    """ 
    Sorts a list of legal moves based on rough estimations
    for which moves are probably good.
    """
    def __init__(self) -> None:
        # MVV_LVA[victim][attacker] = move_score
        # capturing a queen with a pawn has the highest score
        # capturing nothing has the lowest score
        self.MVV_LVA = {
            KING:   {KING:  0, QUEEN:  0, ROOK:  0, BISHOP:  0, KNIGHT:  0, PAWN:  0, None: 0},
            QUEEN:  {KING: 50, QUEEN: 51, ROOK: 52, BISHOP: 53, KNIGHT: 54, PAWN: 55, None: 0},
            ROOK:   {KING: 40, QUEEN: 41, ROOK: 42, BISHOP: 43, KNIGHT: 44, PAWN: 45, None: 0},
            BISHOP: {KING: 30, QUEEN: 31, ROOK: 32, BISHOP: 33, KNIGHT: 34, PAWN: 35, None: 0},
            KNIGHT: {KING: 20, QUEEN: 21, ROOK: 22, BISHOP: 23, KNIGHT: 24, PAWN: 25, None: 0},
            PAWN:   {KING: 10, QUEEN: 11, ROOK: 12, BISHOP: 13, KNIGHT: 14, PAWN: 15, None: 0},
            None:   {KING:  0, QUEEN:  0, ROOK:  0, BISHOP:  0, KNIGHT:  0, PAWN:  0, None: 0},
        }

    def sort(
        self,
        board: chess.Board,
        legal_moves: list[chess.Move],
        pv_move: chess.Move,
        tt_move: chess.Move
    ) -> list[chess.Move]:
        """ Sorts a list of legal moves for a given position based on
        rough estimations for which moves are probably good.

        Args:
            board (chess.Board): Represents the current board state.
            legal_moves (list[chess.Move]): Represents the legal moves for a given position.
            pv_move (chess.Move): Represents the principal variation move.
            tt_move (chess.Move): Represents the move from the transposition table.

        Returns:
            list[chess.Move]: Represents the sorted list of moves.
        """
        def score_move(move: chess.Move) -> int:
            # prioritize moves from the transposition table
            if move == tt_move:
                return 100
            # second priority to pv moves
            elif move == pv_move:
                return 90

            # low priority for quiet moves
            if not board.is_capture(move):
                return 0
            
            attacker = board.piece_type_at(move.from_square)
            victim = board.piece_type_at(move.to_square)

            if board.is_en_passant(move):
                victim = PAWN

            # score each move based on the MVV_LVA heuristic
            return self.MVV_LVA[victim][attacker]
        
        # reverse=True ensures that higher scoring moves are at the front
        return sorted(legal_moves, key=score_move, reverse=True)