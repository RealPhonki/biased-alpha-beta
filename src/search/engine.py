# pylint: disable=line-too-long

# third party
from chess import polyglot
import chess

# project
from src.search.eval_heuristics import MATE_SCORE, INF
from src.search.move_ordering import MoveOrdering
from src.search.evaluation import Evaluation

from src.debug.logger import logger

class SearchAbortionException(Exception):
    """
    Represents the exception raised when the search is canceled during search
    """

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

class TTEntry:
    IS_EXACT = 0
    IS_ALPHA = 1
    IS_BETA = 2

    def __init__(self, depth: int, score: int, flag: int, best_move: chess.Move) -> None:
        self.depth = depth
        self.score = score
        self.flag = flag
        self.best_move = best_move

class Engine:
    """ Evaluates a given board position with alphabeta search """
    def __init__(
        self,
        evaluator: Evaluation,
        move_sorter: MoveOrdering
    ) -> None:
        # instances
        self.evaluator = evaluator
        self.move_sorter = move_sorter
        self.search_ctx = SearchContext()

        # constants
        self.MAX_PLY = 10

        # attributes
        self.TT: dict[int, TTEntry] = {}

    def get_best_move(self, board: chess.Board, max_depth: int) -> chess.Move:
        """ Searches all legal moves for a given position, scores them, and
        returns the move with the highest score.

        Args:
            board (chess.Board): The current position
            depth (int): The depth of the search

        Returns:
            chess.Move: The best move determined by the algorithm
        """

        # the best move is defaulted to the first move before search, but if there are no legal
        # moves that will raise in index error
        if board.is_game_over():
            return None

        self.search_ctx.best_move = None
        self.search_ctx.ply = 0
        self.search_ctx.stop_flag = False

        alpha = -INF
        beta = INF

        for depth in range(1, max_depth + 1):
            self.search_ctx.nodes_searched = 0

            try:
                score = self.search(board, alpha, beta, depth)
            
            except SearchAbortionException():
                logger.log("Search aborted")
                return self.search_ctx.last_best
            
            self.search_ctx.last_best = self.search_ctx.best_move

            self.print_uci(
                depth,
                score,
                self.search_ctx.nodes_searched,
                self.search_ctx.best_move
            )

        return self.search_ctx.best_move
    
    def print_uci(self, depth: int, score: int, nodes: int, best_move: chess.Move) -> None:
        """ Displays search data in uci format

        Args:
            depth (int): Represents the depth of the search.
            score (int): Represents the best score found during search.
            nodes (int): Represents the number of nodes searched.
            best_move (chess.Move): Represents the best move found during search.
        """
        if abs(score) > MATE_SCORE - self.MAX_PLY:
            mate = abs(score) - MATE_SCORE if score > 0 else MATE_SCORE - abs(score)
            text = f"info depth {depth} score mate {mate} nodes {nodes} pv {best_move}"
        else:
            text = f"info depth {depth} score cp {score} nodes {nodes} pv {best_move}"
        
        print(text)
        logger.log(text)

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
            return self.evaluator.evaluate(board, self.search_ctx.ply)

        # maximum depth reached return quiescence
        if depth == 0:
            return self.quiescence(board, alpha, beta)

        key = polyglot.zobrist_hash(board)
        entry = self.TT.get(key)
        if entry and entry.depth >= depth:
            if entry.flag == TTEntry.IS_EXACT:
                return entry.score
            elif entry.flag == TTEntry.IS_ALPHA:
                alpha = max(alpha, entry.score)
            elif entry.flag == TTEntry.IS_BETA:
                beta = min(beta, entry.score)
            
            if alpha >= beta:
                return entry.score
        
        original_alpha = alpha # TODO: figure out what the purpose of this is
        best_score = -INF
        best_move = None

        tt_move = entry.best_move if entry else None
        if self.search_ctx.ply == 0 and self.search_ctx.best_move:
            legal_moves = self.move_sorter.sort(
                board,
                board.legal_moves,
                pv_move=best_move,
                tt_move=tt_move
            )
        else:
            legal_moves = self.move_sorter.sort(
                board,
                board.legal_moves,
                pv_move=None,
                tt_move=tt_move
            )

        # play each legal move and score them
        for move in legal_moves:
            self.search_ctx.ply += 1
            board.push(move)

            # negate the score from the last iteration, a good move for our opponent is bad for us
            score = -self.search(board, -beta, -alpha, depth - 1)

            board.pop()
            self.search_ctx.ply -= 1
            
            if self.search_ctx.stop_flag:
                raise SearchAbortionException()

            # store the best score
            if score > best_score:
                best_score = score
                best_move = move
                
                # insert pv move
                if self.search_ctx.ply == 0:
                    self.search_ctx.best_move = move

            # this position is too good, the opponent had a better move
            # earlier so calculating more is a waste of time (e.g calculating a bunch
            # of captures but assuming the opponent won't recapture)
            if score >= beta:
                self.TT[key] = TTEntry(depth, score, TTEntry.IS_BETA, move)
                return score

            # remember this score and ignore future moves that score lower
            alpha = max(alpha, score)
        
        if best_score <= original_alpha:
            self.TT[key] = TTEntry(depth, best_score, TTEntry.IS_ALPHA, best_move)
        else:
            self.TT[key] = TTEntry(depth, best_score, TTEntry.IS_EXACT, best_move)

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
            raise SearchAbortionException()
        
        self.search_ctx.nodes_searched += 1 # debug

        # stand pat, ref: https://www.chessprogramming.org/Quiescence_Search
        best_score = self.evaluator.evaluate(board, self.search_ctx.ply)
        if self.search_ctx.ply == self.MAX_PLY or best_score >= beta:
            return best_score
        if best_score > alpha:
            alpha = best_score

        legal_moves = self.move_sorter.sort(board, board.generate_legal_captures(), pv_move=None, tt_move=None)

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
    test_board = chess.Board()
    alphabeta = Engine(Evaluation(), MoveOrdering())

    # profile alphabeta
    time, _ = profile(alphabeta.get_best_move, [test_board, 6])

    print(f"Time Elapsed: {time:.3f}s")
    print(f"NPS: {(alphabeta.search_ctx.nodes_searched / time):,.3f}")
    print(f"TT size: {len(alphabeta.TT)}")