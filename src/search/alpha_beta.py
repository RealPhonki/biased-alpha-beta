# third party
import chess

# project
from src.evaluation.pipeline import EvaluationPipeline
from src.evaluation.base import Evaluator, Eval

from src.move_ordering.pipeline import MoveSortingPipeline
from src.move_ordering.mvv_lva import MoveSorter, MvvLva

from src.debug.logger import logger

class SearchContext:
    def __init__(self) -> None:
        self.best_move = None
        self.nodes_searched = 0
        self.ply = 0
        self.stop_flag = False

class AlphaBeta:
    """ Evaluates a given board position with alphabeta search """
    def __init__(
        self,
        evaluation_pipeline: Evaluator,
        move_sorting_pipeline: MoveSorter
    ) -> None:
        self.evaluator = evaluation_pipeline
        self.move_sorter = move_sorting_pipeline
        self.search_ctx = SearchContext()

    def get_best_move(self, board: chess.Board, max_depth: int) -> chess.Move:
        """ Searches all legal moves for a given position, scores them, and
        returns the move with the highest score.

        Args:
            board (chess.Board): The current position
            depth (int): The depth of the search

        Returns:
            chess.Move: The best move determined by the algorithm
        """

        self.search_ctx.best_move = list(board.legal_moves)[0]
        self.search_ctx.nodes_searched = 0
        self.search_ctx.stop_flag = False

        alpha = -1_000_000
        beta = 1_000_000

        for depth in range(1, max_depth + 1):
            score = self.search(board, alpha, beta, depth)

            if self.search_ctx.stop_flag:
                break

            print(f"info depth {depth} score cp {score} pv {self.search_ctx.best_move}")
            logger.log(f"info depth {depth} score cp {score} pv {self.search_ctx.best_move}")

        return self.search_ctx.best_move

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
        # check if the search is canceled
        if self.search_ctx.stop_flag:
            return 499

        self.search_ctx.nodes_searched += 1 # debug

        # if the game is over then return the board evaluation
        if board.is_game_over():
            return self.evaluator.evaluate(board)

        # maximum depth reached return quiescence
        if depth == 0:
            return self.quiescence(board, alpha, beta)

        # default the best score to some low value
        best_score = -1_000_000

        # if this is the root position then prioritize the pv move (from previous iterations)
        if self.search_ctx.ply == 0 and self.search_ctx.best_move:
            legal_moves = self.move_sorter.sort(board, board.legal_moves, self.search_ctx.best_move)
        else:
            legal_moves = self.move_sorter.sort(board, board.legal_moves, None)

        # play each legal move and score them
        for move in legal_moves:
            self.search_ctx.ply += 1

            # negate the score from the last iteration, a good move for our opponent is bad for us
            board.push(move)
            score = -self.search(board, -beta, -alpha, depth - 1)
            board.pop()

            self.search_ctx.ply -= 1

            # store the best score
            if score > best_score:
                best_score = score
                
                # insert pv move
                if self.search_ctx.ply == 0:
                    self.search_ctx.best_move = move

            # this position is too good, the opponent had a better move
            # earlier and won't choose this path (e.g calculating a bunch
            # of captures but assuming the opponent won't recapture)
            if score >= beta:
                return best_score

            # remember this score and ignore future moves that score lower
            alpha = max(alpha, score)
        
        return best_score
    
    def quiescence(self, board: chess.Board, alpha: int, beta: int) -> Eval:
        """ Performs a search of all captures and checks

        Args:
            board (chess.Board): The current board state.
            alpha (int): The best score we can guarantee.
            beta (int): The best score the opponent can guarantee.
            depth (int): The current depth of the search.

        Returns:
            Eval: The evaluation determined by the evaluator.
        """
        # check if the search is canceled
        if self.search_ctx.stop_flag:
            return 499

        self.search_ctx.nodes_searched += 1 # debug

        # stand pat, ref: https://www.chessprogramming.org/Quiescence_Search
        best_score = self.evaluator.evaluate(board)
        if best_score >= beta:
            return best_score
        if best_score > alpha:
            alpha = best_score

        legal_moves = self.move_sorter.sort(board, board.generate_legal_captures(), pv_move=None)

        # play each legal capture and score them
        for move in legal_moves:
            # negate the score from the last iteration, a good move for our opponent is bad for us
            board.push(move)
            score = -self.quiescence(board, -beta, -alpha)
            board.pop()

            # store the best score
            best_score = max(best_score, score)

            # this position is too good, the opponent had a better move
            # earlier and won't choose this path (e.g calculating a bunch
            # of captures but assuming the opponent won't recapture)
            if score >= beta:
                return best_score

            # remember this score and ignore future moves that score lower
            alpha = max(alpha, score)
        
        return best_score

if __name__ == "__main__":
    from src.evaluation.material import MaterialEvaluator
    from src.debug.profiler import profile

    # create instances
    test_board = chess.Board("rnbqk2r/ppp1Pppp/8/2b5/8/5N2/PPP1PPPP/RNBQKB1R b KQkq - 0 5")
    eval_pipeline = EvaluationPipeline(MaterialEvaluator())
    sort_pipeline = MoveSortingPipeline(MvvLva())
    alphabeta = AlphaBeta(eval_pipeline, sort_pipeline)

    # profile alphabeta
    time, _ = profile(alphabeta.get_best_move, [test_board, 6])

    print(f"Time Elapsed: {time:.3f}s")
    print(f"NPS: {(alphabeta.search_ctx.nodes_searched / time):,.3f}")