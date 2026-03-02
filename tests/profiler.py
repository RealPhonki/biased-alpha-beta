# standard
import cProfile

# third party
import chess

# project
from src.search.move_ordering import MoveOrdering
from src.search.evaluation import Evaluation
from src.search.engine import Engine

from src.search.legacy_engine import Engine as Legacy

if __name__ == "__main__":
    # create instances
    engine = Engine(Evaluation(), MoveOrdering())
    legacy = Legacy(Evaluation(), MoveOrdering())
    profiler = cProfile.Profile()
    test_board = chess.Board()

    # start profiling
    profiler.enable()

    engine.get_best_move(test_board, 5)

    # end profiling
    profiler.disable()
    profiler.dump_stats("tests/engine_profile.prof")

    # start profiling
    profiler.enable()

    legacy.get_best_move(test_board, 5)

    # end profiling
    profiler.disable()
    profiler.dump_stats("tests/legacy_profile.prof")