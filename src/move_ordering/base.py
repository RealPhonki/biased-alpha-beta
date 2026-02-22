# third party
import chess

class MoveSorter:
    """
    This is the parent class for all move sorters. Move sorters must have an sort method that
    takes the board position, and a list of legal moves; and returns a new list of moves.
    """

    def sort(self, board: chess.Board, legal_moves: list[chess.Move]) -> list[chess.Move]:
        """ Sorts a list of legal chess moves given a position.

        Args:
            legal_moves (list[chess.Move]): The list of legal moves.

        Returns:
            list[chess.Move]: The sorted list of legal moves.
        """