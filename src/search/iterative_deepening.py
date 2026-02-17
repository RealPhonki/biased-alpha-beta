# pylint: disable=line-too-long

# standard
from typing import Tuple

# third party
import chess

# project
from src.evaluation.pipeline import EvaluationPipeline
from src.evaluation.base import Eval

class AlphaBeta:
    """ Evaluates a given board position with alphabeta search """
    def __init__(self, evaluation_pipeline: EvaluationPipeline) -> None:
        self.nodes_searched = 0
        self.evaluator = evaluation_pipeline

    def get_best_move(self, board: chess.Board, max_depth: int) -> chess.Move:
        """ Finds the best move by applying iterative deepening.

        Args:
            board (chess.Board): The current board state
            max_depth (int): The maximum depth to search

        Returns:
            chess.Move: The current best move
        """
        self.nodes_searched = 0

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        curr_best_move = legal_moves[0]

        for curr_depth in range(1, max_depth + 1):
            curr_best_move, score = self.search_root(board, curr_depth, curr_best_move)

            print(f"info depth {curr_depth} score cp {score} pv {curr_best_move.uci()} nodes {self.nodes_searched}")

        return curr_best_move

    def search_root(self, board: chess.Board, depth: int, pv_move: chess.Move) -> Tuple[chess.Move, Eval]:
        """ Searches all legal moves for a given position, scores them, and
        returns the move with the highest score.

        Args:
            board (chess.Board): The current position
            depth (int): The depth of the search

        Returns:
            chess.Move: The best move determined by the algorithm
        """
        best_score = -1_000_000
        alpha = -1_000_000
        beta = 1_000_000

        legal_moves = list(board.legal_moves)
        if pv_move in legal_moves:
            legal_moves.insert(0, legal_moves.pop(legal_moves.index(pv_move)))

        best_move = legal_moves[0]

        for move in legal_moves:
            board.push(move)
            score = -self.search(board, -beta, -alpha, depth - 1)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)

        return best_move, best_score

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
            return self.evaluator.evaluate(board)

        # play each legal move and score them
        best_score = -1_000_000

        legal_moves = list(board.legal_moves) # TODO: apply move ordering later

        for move in legal_moves:
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

    # create instances
    test_board = chess.Board("r1bqkb1r/pp2nppp/2P5/1B2p3/4n3/2P5/PP3PPP/RNBQK2R w KQkq - 0 9")
    pipeline = EvaluationPipeline(
        MaterialEvaluator()
    )
    alphabeta = AlphaBeta(pipeline)

    # profile alphabeta
    time, _ = profile(alphabeta.get_best_move, [test_board, 5])

    print(f"Time Elapsed: {time:.3f}s")
    print(f"NPS: {(alphabeta.nodes_searched / time):,.3f}")