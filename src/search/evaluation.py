# third party
import chess

# project
from src.search.eval_heuristics import BLACK_MG_PESTO_TABLE, BLACK_EG_PESTO_TABLE, WHITE_MG_PESTO_TABLE, WHITE_EG_PESTO_TABLE, PHASE_VALUE, MATE_SCORE

class Evaluation:
    """
    Returns the relative evaluation for a given board state.
    """
    def __init__(self) -> None:
        self.PIECES = [chess.PAWN, chess.BISHOP, chess.KNIGHT, chess.ROOK, chess.QUEEN, chess.KING]

    def count_material(self, board: chess.Board) -> int:
        """
        Returns the material difference for a given chess position as an absolute evaluation.
        The value of each piece is skewed based on its location.

        Args:
            board (chess.Board): Represents the current board state.

        Returns:
            int: Represents the evaluation.
        """
        mg_white = 0
        eg_white = 0
        mg_black = 0
        eg_black = 0
        game_phase = 0

        # evaluate each piece
        for piece_type in self.PIECES:
            for square in board.pieces(piece_type, chess.WHITE):
                game_phase += PHASE_VALUE[piece_type]
                mg_white += WHITE_MG_PESTO_TABLE[piece_type][square]
                eg_white += WHITE_EG_PESTO_TABLE[piece_type][square]
            
            for square in board.pieces(piece_type, chess.BLACK):
                game_phase += PHASE_VALUE[piece_type]
                mg_black += BLACK_MG_PESTO_TABLE[piece_type][square]
                eg_black += BLACK_EG_PESTO_TABLE[piece_type][square]

        # calculate tapered evaluation
        mg_score = mg_white - mg_black
        eg_score = eg_white - eg_black
        mg_phase = min(game_phase, 24)
        eg_phase = 24 - mg_phase
        return (mg_score * mg_phase + eg_score * eg_phase) // 24
    
    def evaluate_checkmate(self, board: chess.Board, ply) -> int:
        """
        Returns the evaluation for a position in checkmate where shorter checkmates
        have higher scores. This method uses the negation of this formula: MATE_SCORE - ply

        Args:
            board (chess.Board): Represents the current board state.
            ply (_type_): Represents the distance from the root position.

        Returns:
            int: Represents the score for the given checkmate.
        """
        if board.is_checkmate():
            return -MATE_SCORE + ply
        return 0

    def evaluate(self, board: chess.Board) -> int:
        """
        Returns the relative evaluation for a given board state where negative is bad
        and positive is good.

        Args:
            board (chess.Board): Represents the current boards state.

        Returns:
            int: Represents the evaluation.
        """
        score = 0

        score += self.count_material(board)

        return score if board.turn == chess.WHITE else -score

if __name__ == "__main__":
    test_board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R2QKBNR w KQkq - 0 1")
    evaluator = Evaluation()
    print(evaluator.evaluate(test_board))