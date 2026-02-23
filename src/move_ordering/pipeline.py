# third party
import chess

# project
from src.move_ordering.base import MoveSorter

class MoveSortingPipeline(MoveSorter):
    """
    Applies all sorting algorithms by all move sorters.
    """
    def __init__(self, *move_sorters: MoveSorter) -> None:
        self.move_sorters = move_sorters

    def sort(self, board: chess.Board, legal_moves: list[chess.Move]) -> list[chess.Move]:
        sorted_moves = list(legal_moves)
        for move_sorter in self.move_sorters:
            sorted_moves = move_sorter.sort(board, sorted_moves)
        
        return sorted_moves