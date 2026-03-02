# third party
import chess

# project
from src.search.eval_heuristics import MG_PESTO_TABLE, MATE_SCORE

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
        score = 0

        for square in board.pieces(chess.PAWN, chess.WHITE):
            score += MG_PESTO_TABLE[chess.PAWN][chess.square_mirror(square)]

        for square in board.pieces(chess.PAWN, chess.BLACK):
            score -= MG_PESTO_TABLE[chess.PAWN][square]
        
        for square in board.pieces(chess.KNIGHT, chess.WHITE):
            score += MG_PESTO_TABLE[chess.KNIGHT][chess.square_mirror(square)]

        for square in board.pieces(chess.KNIGHT, chess.BLACK):
            score -= MG_PESTO_TABLE[chess.KNIGHT][square]

        for square in board.pieces(chess.BISHOP, chess.WHITE):
            score += MG_PESTO_TABLE[chess.BISHOP][chess.square_mirror(square)]

        for square in board.pieces(chess.BISHOP, chess.BLACK):
            score -= MG_PESTO_TABLE[chess.BISHOP][square]

        for square in board.pieces(chess.ROOK, chess.WHITE):
            score += MG_PESTO_TABLE[chess.ROOK][chess.square_mirror(square)]

        for square in board.pieces(chess.ROOK, chess.BLACK):
            score -= MG_PESTO_TABLE[chess.ROOK][square]

        for square in board.pieces(chess.QUEEN, chess.WHITE):
            score += MG_PESTO_TABLE[chess.QUEEN][chess.square_mirror(square)]

        for square in board.pieces(chess.QUEEN, chess.BLACK):
            score -= MG_PESTO_TABLE[chess.QUEEN][square]

        for square in board.pieces(chess.KING, chess.WHITE):
            score += MG_PESTO_TABLE[chess.KING][chess.square_mirror(square)]

        for square in board.pieces(chess.KING, chess.BLACK):
            score -= MG_PESTO_TABLE[chess.KING][square]

        return score
    
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