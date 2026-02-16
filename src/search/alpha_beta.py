# pylint: disable=trailing-whitespace
# pylint: disable=missing-module-docstring
# pylint: disable=missing-final-newline
# pylint: disable=wildcard-import
# pylint: disable=import-error

# third party
import chess

# project
from src.evaluation.pipeline import EvaluationPipeline
from src.evaluation.base import Eval

from src.debug.profiler import profile

class AlphaBeta:
    """ Evaluates a given board position with minimax search """
    def __init__(self, evaluation_pipeline: EvaluationPipeline) -> None:
        self.leaves_searched = 0
        self.nodes_searched = 0
        self.evaluator = evaluation_pipeline

    def search(self, board: chess.Board, depth: int) -> Eval:
        """ Performs a minimax search recursively.

        Args:
            board (chess.Board): The current board state.
            depth (int): The current depth of the search.

        Returns:
            Eval: The evaluation determined by the evaluator.
        """
        self.nodes_searched += 1 # debug

        # maximum depth reached or game is over, return evaluation
        if depth == 0 or board.is_game_over():
            self.leaves_searched += 1 # debug
            return self.evaluator.evaluate(board)

        # play each legal move and score them
        best_score = -100_000
        for move in board.legal_moves:
            board.push(move)
            score = -self.search(board, depth - 1)
            board.pop()

            # store the best score
            best_score = max(best_score, score)
        
        return best_score

if __name__ == "__main__":
    from src.evaluation.material import MaterialEvaluator

    # create instances
    test_board = chess.Board("r3r1k1/ppp2ppp/3p4/3P4/1PP3n1/2N5/1P1BNPPq/R2QRK2 b - - 1 2")
    pipeline = EvaluationPipeline(
        MaterialEvaluator()
    )
    search = AlphaBeta(pipeline)

    # execute method
    time, test_score = profile(search.search, [test_board, 3])

    # debug
    print("-"*32)
    print(f"Score: {test_score:,}")
    print(f"Nodes: {search.nodes_searched:,}")
    print(f"Leaves: {search.leaves_searched:,}")
    print(f"Time Elapsed: {time:.3f}s")
    print(f"NPS: {(search.nodes_searched / time):,.3f}")