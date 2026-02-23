# third party
import chess

# project
from src.evaluation.pipeline import EvaluationPipeline
from src.evaluation.base import Evaluator, Eval

from src.move_ordering.pipeline import MoveSortingPipeline
from src.move_ordering.mvv_lva import MoveSorter, MvvLva

class AlphaBeta:
    """ Evaluates a given board position with alphabeta search """
    def __init__(
        self,
        evaluation_pipeline: Evaluator,
        move_sorting_pipeline: MoveSorter
    ) -> None:
        self.nodes_searched = 0
        self.evaluator = evaluation_pipeline
        self.move_sorter = move_sorting_pipeline

    def get_best_move(self, board: chess.Board, depth: int) -> chess.Move:
        """ Searches all legal moves for a given position, scores them, and
        returns the move with the highest score.

        Args:
            board (chess.Board): The current position
            depth (int): The depth of the search

        Returns:
            chess.Move: The best move determined by the algorithm
        """

        self.nodes_searched = 0

        best_score = -100_000
        alpha = -100_000
        beta = 100_000

        legal_moves = self.move_sorter.sort(board, board.legal_moves)

        best_move = legal_moves[0]

        for move in legal_moves:
            board.push(move)
            score = -self.search(board, -beta, -alpha, depth - 1)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)

            # required by uci
            print(f"info depth {depth} score cp {int(best_score)} pv {best_move.uci()}")

        return best_move

    def search(self, board: chess.Board, alpha: int, beta: int, depth: int) -> Eval:
        """ Performs an alphabeta search recursively.

        Args:
            board (chess.Board): The current board state.
            alpha (int): The best score we can guarantee.
            beta (int): The best score the opponent can guarantee.
            depth (int): The current depth of the search.

        Returns:
            Eval: The evaluation determined by the evaluator.
        """
        self.nodes_searched += 1 # debug

        # maximum depth reached or game is over, return evaluation
        if depth == 0 or board.is_game_over():
            return self.evaluator.evaluate(board)

        # default the best score to some low value
        best_score = -100_000
        legal_moves = self.move_sorter.sort(board, board.legal_moves)

        # play each legal move and score them
        for move in legal_moves:
            # negate the score from the last iteration, a good move for our opponent is bad for us
            board.push(move)
            score = -self.search(board, -beta, -alpha, depth - 1)
            board.pop()

            # store the best score
            best_score = max(best_score, score)

            # remember this score and ignore future moves that score lower
            alpha = max(alpha, score)

            # this position is too good, the opponent had a better move
            # earlier and won't choose this path (e.g calculating a bunch
            # of captures but assuming the opponent won't recapture)
            if score >= beta:
                return best_score
        
        return best_score

if __name__ == "__main__":
    from src.evaluation.material import MaterialEvaluator
    from src.debug.profiler import profile

    # create instances
    test_board = chess.Board("1r2r1k1/5ppp/8/8/q7/4R3/4QPPP/4RK2 w - - 0 1")
    eval_pipeline = EvaluationPipeline(MaterialEvaluator())
    sort_pipeline = MoveSortingPipeline(MvvLva())
    alphabeta = AlphaBeta(eval_pipeline, sort_pipeline)

    # profile alphabeta
    time, _ = profile(alphabeta.get_best_move, [test_board, 3])

    print(f"Time Elapsed: {time:.3f}s")
    print(f"NPS: {(alphabeta.nodes_searched / time):,.3f}")