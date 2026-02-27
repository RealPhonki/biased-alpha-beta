# standard
import cProfile

# third party
import chess

# project
from src.search.move_ordering import MoveOrdering
from src.search.evaluation import Evaluation
from src.search.engine import Engine

if __name__ == "__main__":
    # create instances
    engine = Engine(Evaluation(), MoveOrdering())
    profiler = cProfile.Profile()
    test_board = chess.Board()

    # start profiling
    profiler.enable()

    engine.get_best_move(test_board, 5)

    # end profiling
    profiler.disable()
    profiler.dump_stats("tests/profile.prof")