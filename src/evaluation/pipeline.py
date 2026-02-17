# third party
import chess

# project
from src.evaluation.base import Evaluator, Eval

class EvaluationPipeline(Evaluator):
    """
    Returns the sum of the evaluations made by all evaluators. 
    All evaluations are overridden if the game is over.
    """
    def __init__(self, *evaluators: list[Evaluator]) -> None:
        self.evaluators = evaluators

    def evaluate(self, board: chess.Board) -> Eval:
        # override evaluation if the game is over
        if board.is_game_over():
            if board.is_checkmate():
                # If white loses the score is -100,000.
                # If black loses the score is 100,000, but is negated later anyways.
                return -100_000
            return 0

        # calculate the absolute score if the game is not over
        score = 0
        for evaluator in self.evaluators:
            score += evaluator.evaluate(board)
        
        # correct perspective for negamax
        if board.turn == chess.WHITE:
            return score
        else:
            return -score

if __name__ == "__main__":
    pass