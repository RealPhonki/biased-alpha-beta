# third party
import chess

class MoveSorter:
    """
    This is the parent class for all move sorters. Move sorters must have an sort method that
    takes the board position, and a list of legal moves; and returns a new list of moves.
    """

    def sort(
        self, 
        board: chess.Board, 
        legal_moves: list[chess.Move], 
        pv_move: chess.Move
    ) -> list[chess.Move]:
        """ Sorts a list of legal chess moves given a position.

        Args:
            board (chess.Board): The current board state.
            legal_moves (list[chess.Move]): The list of legal moves.
            pv_move (chess.Move): The principle variation move (which will be prioritized)

        Returns:
            list[chess.Move]: The sorted list of legal moves.
        """