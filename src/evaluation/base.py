# third party
import chess

Eval = int

class Evaluator:
    """
    This is the parent class for all evaluators. Evaluators must have an evaluate method that
    takes in a board position and returns a float.
    """
    def evaluate(self, board: chess.Board)  -> Eval:
        """ Returns an evaluation for a given board position

        Args:
            board (chess.Board): The board state

        Returns:
            Eval: The evaluation
        """