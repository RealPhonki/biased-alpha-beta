# third party
import chess

class Evaluation:
    """
    Returns the relative evaluation for a given board state.
    """
    def __init__(self) -> None:
        self.PIECES = [chess.PAWN, chess.BISHOP, chess.KNIGHT, chess.ROOK, chess.QUEEN, chess.KING]
        self.PIECE_VALUES = {
            chess.PAWN: 100,
            chess.BISHOP: 300,
            chess.KNIGHT: 300,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }

    def count_material(self, board: chess.Board) -> int:
        """
        Returns the material difference for a given chess position as an absolute evaluation.

        Args:
            board (chess.Board): Represents the board state.

        Returns:
            int: Represents the material difference.
        """
        white_material = 0
        black_material = 0

        for piece_type in self.PIECES:
            value = self.PIECE_VALUES[piece_type]

            white_material += len(board.pieces(piece_type, chess.WHITE)) * value
            black_material += len(board.pieces(piece_type, chess.BLACK)) * value

        return white_material - black_material

    def evaluate(self, board: chess.Board, ply: int) -> int:
        """
        Returns the relative evaluation for a given board state.

        Args:
            board (chess.Board): Represents the board state.

        Returns:
            int: Represents the evaluation.
        """
        if board.is_game_over():
            if board.is_checkmate():
                # in a negamax framework, positive is always good and negative is always bad
                # because the score perspective is adjusted at every ply
                return -100_000 + ply
            return 0

        score = 0

        score += self.count_material(board)

        return score if board.turn == chess.WHITE else -score