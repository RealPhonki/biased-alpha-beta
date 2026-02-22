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

        legal_moves = list(board.legal_moves)

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
            depth (int): The current depth of the search.

        Returns:
            Eval: The evaluation determined by the evaluator.
        """
        self.nodes_searched += 1 # debug

        # maximum depth reached or game is over, return evaluation
        if depth == 0 or board.is_game_over():
            return self.evaluator.evaluate(board)

        # play each legal move and score them
        best_score = -100_000

        legal_moves = list(board.legal_moves)

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
    time, _ = profile(alphabeta.get_best_move, [test_board, 4])

    print(f"Time Elapsed: {time:.3f}s")
    print(f"NPS: {(alphabeta.nodes_searched / time):,.3f}")