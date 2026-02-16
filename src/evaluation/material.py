# third party
import chess

# project
from src.evaluation.base import Evaluator, Eval
from src.debug.profiler import profile

class MaterialEvaluator(Evaluator):
    """ Calculates board evaluation by material only. """

    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.BISHOP: 300,
        chess.KNIGHT: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0
    }

    def evaluate(self, board: chess.Board) -> Eval:
        """ Calculates an absolute evaluation by summing the material value
        of every piece on the board using self.PIECE_VALUES. All black
        pieces are assigned a negative value.

        Args:
            board (chess.Board): The board state to evaluate.

        Returns:
            Eval: The sum of material values.
        """
        white_material = 0
        black_material = 0

        for piece_type in [chess.PAWN, chess.BISHOP, chess.KNIGHT, chess.ROOK, chess.QUEEN]:
            value = self.PIECE_VALUES[piece_type]

            white_material += len(board.pieces(piece_type, chess.WHITE)) * value
            black_material += len(board.pieces(piece_type, chess.BLACK)) * value

        return white_material - black_material

if __name__ == "__main__":
    evaluator = MaterialEvaluator()
    test_board = chess.Board("Q4b1r/p2qkppp/2B5/4p3/4n3/2P5/PP3PPP/RNB1K2R w KQ - 1 13")
    
    time, score = profile(evaluator.evaluate, [test_board], repeat=8902)

    print(f"Time: {time}")
    print(f"Score: {score}")