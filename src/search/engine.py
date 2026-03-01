# third party
import chess

# project
from src.search.move_ordering import MoveOrdering
from src.search.evaluation import Evaluation

from src.debug.logger import logger

class SearchContext:
    """
    This class contains global data that is used during search
    """
    def __init__(self) -> None:
        self.best_move = None
        self.nodes_searched = 0
        self.ply = 0
        self.stop_flag = False

        # temporary handler to force the engine to revert to the best move from
        # the previous iteration if a given iteration is canceled.
        self.last_best = None

class Engine:
    """ Evaluates a given board position with alphabeta search """
    def __init__(
        self,
        evaluator: Evaluation,
        move_sorter: MoveOrdering
    ) -> None:
        self.evaluator = evaluator
        self.move_sorter = move_sorter
        self.search_ctx = SearchContext()

        self.MAX_PLY = 10

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
                logger.log("Search aborted")
                return self.search_ctx.last_best

            self.search_ctx.last_best = self.search_ctx.best_move

            print(f"info depth {depth} score cp {score} pv {self.search_ctx.best_move}")
            logger.log(f"info depth {depth} score cp {score} pv {self.search_ctx.best_move}")

        return self.search_ctx.best_move

    def search(self, board: chess.Board, alpha: int, beta: int, depth: int) -> int:
        """ Performs an alphabeta search recursively.

        Args:
            board (chess.Board): The current board state.
            alpha (int): The best score we can guarantee.
            beta (int): The best score the opponent can guarantee.
            depth (int): The current depth of the search.

        Returns:
            Eval: The evaluation determined by the evaluator.
        """
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

            if self.search_ctx.stop_flag:
                if board.turn == chess.WHITE:
                    # this value will be negated at the previous ply.
                    return 1_000_000
                return -1_000_000

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
    
    def quiescence(self, board: chess.Board, alpha: int, beta: int) -> int:
        """ Performs a search of all captures and checks

        Args:
            board (chess.Board): The current board state.
            alpha (int): The best score we can guarantee.
            beta (int): The best score the opponent can guarantee.
            depth (int): The current depth of the search.

        Returns:
            Eval: The evaluation determined by the evaluator.
        """
        if self.search_ctx.stop_flag:
            if board.turn == chess.WHITE:
                # this value will be negated at the previous ply.
                return 1_000_000
            return -1_000_000
        

        self.search_ctx.nodes_searched += 1 # debug

        # stand pat, ref: https://www.chessprogramming.org/Quiescence_Search
        best_score = self.evaluator.evaluate(board)
        if self.search_ctx.ply == self.MAX_PLY or best_score >= beta:
            return best_score
        if best_score > alpha:
            alpha = best_score

        legal_moves = self.move_sorter.sort(board, board.generate_legal_captures(), pv_move=None)

        # play each legal capture and score them
        for move in legal_moves:
            self.search_ctx.ply += 1

            # negate the score from the last iteration, a good move for our opponent is bad for us
            board.push(move)
            score = -self.quiescence(board, -beta, -alpha)
            board.pop()

            self.search_ctx.ply -= 1

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
    from src.debug.profiler import profile

    # create instances
    test_board = chess.Board("rnbqkbnr/pppp1ppp/8/4p3/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2")
    # info depth 5 nodes 1579993 score cp 0 pv b8a6
    alphabeta = Engine(Evaluation(), MoveOrdering())

    # profile alphabeta
    time, _ = profile(alphabeta.get_best_move, [test_board, 4])

    print(f"Time Elapsed: {time:.3f}s")
    print(f"NPS: {(alphabeta.search_ctx.nodes_searched / time):,.3f}")