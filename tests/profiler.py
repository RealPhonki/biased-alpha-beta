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
    test_board = chess.Board("r1b1k2r/ppp2pp1/2p5/2b1q3/6p1/3P4/PPP1BPP1/RNBQ1RK1 w kq - 0 11")

    # start profiling
    profiler.enable()

    engine.get_best_move(test_board, 4)

    # end profiling
    profiler.disable()
    profiler.dump_stats("tests/engine_profile.prof")

    # start profiling
    profiler.enable()

    legacy.get_best_move(test_board, 4)

    # end profiling
    profiler.disable()
    profiler.dump_stats("tests/legacy_profile.prof")