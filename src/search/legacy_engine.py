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

    Attributes:
        best_move (chess.Move): Represents the best move found during search.
        nodes_searched (int): Represents the number of nodes searched.
        ply (int): Represents the current depth where the root position is depth 0.
        stop_flag (bool): This flag can be set to true in order to terminate search early.
        last_best (chess.Move): Represents the best move found in the previous search.
                    When a search is terminated this is the move returned in uci.
    """
    def __init__(self) -> None:
        self.best_move = None
        self.nodes_searched = 0
        self.ply = 0
        self.stop_flag = False
        self.last_best = None

class TTEntry:
    """
    When positions are searched, the best move and metadata are stored as transposition
    table entries in a hashmap where the key is a hash of the position. This is used to
    avoid evaluating the same position twice during search.

    However, because search can be canceled for two different reasons (fail high and fail low),
    There are three types of TTEntries which are represented with various flags.

    Attributes:
        depth (int): Represents the depth that the entry was originally found in.
        score (int): Represents the evaluated score of the position for this entry.
        flag (int): Represents the type of transposition table entry this is.
        best_move (chess.Move): Represents the best move in the position.
    """

    # flags
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
        """
        Performs iterative deepening on a given board state and displays search information
        as uci.

        Args:
            board (chess.Board): Represents the current board state.
            max_depth (int): Represents the maximum depth to search.

        Returns:
            chess.Move: Represents the best move found during search.
        """
        # reset search context from previous searches to prevent data leakage
        self.search_ctx.best_move = None
        self.search_ctx.stop_flag = False

        # increase depth with each iteration
        for depth in range(1, max_depth + 1):
            # reset search context from previous iterations to prevent data leakage
            self.search_ctx.nodes_searched = 0
            self.search_ctx.ply = 0
            alpha = -INF
            beta = INF

            try:
                score = self.search(board, alpha, beta, depth)
            
            # search canceled, return the best move found in the previous iteration
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
        """
        Performs alpha beta search with the following optimizations:
        - quiescence search
        - transposition table and move ordering

        Args:
            board (chess.Board): Represents the current board state.
            alpha (int): Represents the best (highest) score the current side can guarantee.
            beta (int): Represents the best (lowest) score the opposing side can guarantee.
            depth (int): Represents the current depth of the search.

        Raises:
            SearchAbortionException: This exception is raised if the search is canceled.
                                     This can be done via 'search_ctx.stop_flag = True'

        Returns:
            int: Represents the best score found for the given position.
        """
        # if the stop flag is true then cancel the search
        if self.search_ctx.stop_flag:
            raise SearchAbortionException()
        
        self.search_ctx.nodes_searched += 1

        # if the game is over then return the board evaluation
        if board.is_game_over():
            return self.evaluator.evaluate_checkmate(board, self.search_ctx.ply)

        # if the maximum depth is reached return the evaluation from the quiescence search
        if depth == 0:
            return self.quiescence(board, alpha, beta)

        # look up this position in the transposition table
        key = polyglot.zobrist_hash(board)
        entry = self.TT.get(key)

        # if the position is found then either return the score or adjust
        # fail highs and lows
        if entry and entry.depth >= depth:
            if entry.flag == TTEntry.IS_EXACT:
                return entry.score
            elif entry.flag == TTEntry.IS_ALPHA:
                alpha = max(alpha, entry.score)
            elif entry.flag == TTEntry.IS_BETA:
                beta = min(beta, entry.score)
            
            if alpha >= beta:
                return entry.score

        # prioritize pv move and tt moves in move ordering
        tt_move = entry.best_move if entry else None
        if self.search_ctx.ply == 0 and self.search_ctx.best_move:
            legal_moves = self.move_sorter.sort(
                board,
                board.legal_moves,
                pv_move=self.search_ctx.best_move, # TODO: replace this crude pv move implementation
                tt_move=tt_move
            )
        else:
            legal_moves = self.move_sorter.sort(
                board,
                board.legal_moves,
                pv_move=None,
                tt_move=tt_move
            )

        original_alpha = alpha
        best_score = -INF
        best_move = None

        for move in legal_moves:
            self.search_ctx.ply += 1
            board.push(move)

            # negate the score from the last iteration, a good move for our opponent is bad for us
            score = -self.search(board, -beta, -alpha, depth - 1)

            board.pop()
            self.search_ctx.ply -= 1

            # store the best score
            if score > best_score:
                best_score = score
                best_move = move
                
                # insert pv move if we are at the root
                if self.search_ctx.ply == 0:
                    self.search_ctx.best_move = move

            # this position is too good, the opponent had a better move earlier (fail high)
            if score >= beta:
                self.TT[key] = TTEntry(depth, score, TTEntry.IS_BETA, move)
                return score

            # remember this score and ignore future moves that score lower
            alpha = max(alpha, score)
        
        # store transposition table data
        # TODO: correct this documentation
        if best_score <= original_alpha:
            self.TT[key] = TTEntry(depth, best_score, TTEntry.IS_ALPHA, best_move)
        else:
            self.TT[key] = TTEntry(depth, best_score, TTEntry.IS_EXACT, best_move)

        return best_score
    
    def quiescence(self, board: chess.Board, alpha: int, beta: int) -> int:
        """
        Performs a search of only captures for a given board state.

        Args:
            board (chess.Board): Represents the current board state.
            alpha (int): Represents the best (highest) score that the current side can guarantee.
            beta (int): Represents the best (lowest) score that the opposing side can guarantee.

        Raises:
            SearchAbortionException: This exception is raised if the search is canceled.
                                     This can be done via 'search_ctx.stop_flag = True'

        Returns:
            int: Represents the best score found during search.
        """
        # if the stop flag is true then cancel the search
        if self.search_ctx.stop_flag:
            raise SearchAbortionException()
        
        self.search_ctx.nodes_searched += 1

        # stand pat, ref: https://www.chessprogramming.org/Quiescence_Search
        best_score = self.evaluator.evaluate(board)
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

            # this position is too good, the opponent had a better move earlier (fail high)
            if score >= beta:
                return best_score

            # remember this score and ignore future moves that score lower
            alpha = max(alpha, score)
        
        return best_score

if __name__ == "__main__":
    from src.debug.profiler import profile

    # create instances
    test_board = chess.Board("1rr1r2k/5ppp/6q1/8/Q7/4R3/4RPPP/4R2K w - - 0 1")
    alphabeta = Engine(Evaluation(), MoveOrdering())

    # profile alphabeta
    time, _ = profile(alphabeta.get_best_move, [test_board, 4])

    print(f"Time Elapsed: {time:.3f}s")
    print(f"NPS: {(alphabeta.search_ctx.nodes_searched / time):,.3f}")
    print(f"TT size: {len(alphabeta.TT)}")