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

class AlphaBeta:
    """ Evaluates a given board position with alphabeta search """
    def __init__(self, evaluation_pipeline: EvaluationPipeline) -> None:
        self.leaves_searched = 0
        self.nodes_searched = 0
        self.evaluator = evaluation_pipeline

    def search(self, board: chess.Board, alpha: int, beta: int, depth: int) -> Eval:
        """ Performs an alphabeta search recursively.

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
            score = -self.search(board, -beta, -alpha, depth - 1)
            board.pop()

            # store the best score
            best_score = max(best_score, score)
            alpha = max(alpha, score)

            if score >= beta:
                return best_score
        
        return best_score

if __name__ == "__main__":
    from src.evaluation.material import MaterialEvaluator
    from src.debug.profiler import profile

    from src.search.min_max import MinMax

    # create instances
    test_board = chess.Board("r1bqk2r/pppp1Npp/2n2n2/2b1p3/2B1P3/8/PPPP1PPP/RNBQK2R b KQkq - 0 5")
    pipeline = EvaluationPipeline(
        MaterialEvaluator()
    )
    alphabeta = AlphaBeta(pipeline)
    minmax = MinMax(pipeline)

    # profile alphabeta
    ab_time, ab_test_score = profile(alphabeta.search, [test_board, -100_000, 100_000, 3])

    print("-"*16 + " ALPHABETA" + "-"*16)
    print(f"Score: {ab_test_score:,}")
    print(f"Nodes: {alphabeta.nodes_searched:,}")
    print(f"Leaves: {alphabeta.leaves_searched:,}")
    print(f"Time Elapsed: {ab_time:.3f}s")
    print(f"NPS: {(alphabeta.nodes_searched / ab_time):,.3f}")

    print()

    # profile minmax
    mm_time, mm_test_score = profile(minmax.search, [test_board, 3])

    print("-"*16 + " MINMAX" + "-"*16)
    print(f"Score: {mm_test_score:,}")
    print(f"Nodes: {minmax.nodes_searched:,}")
    print(f"Leaves: {minmax.leaves_searched:,}")
    print(f"Time Elapsed: {mm_time:.3f}s")
    print(f"NPS: {(minmax.nodes_searched / mm_time):,.3f}")