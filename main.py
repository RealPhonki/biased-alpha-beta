# pylint: disable=broad-exception-caught

# standard
import sys

# third party
import chess

# project
from src.move_ordering.pipeline import MoveSortingPipeline
from src.move_ordering.mvv_lva import MvvLva

from src.evaluation.pipeline import EvaluationPipeline
from src.evaluation.material import MaterialEvaluator

from src.search.alpha_beta import AlphaBeta

from src.debug.logger import logger

class CommandError(Exception):
    ...

class UCIHandler:
    def __init__(self) -> None:
        # subclasses
        self.eval_pipeline = EvaluationPipeline(MaterialEvaluator())
        self.sort_pipeline = MoveSortingPipeline(MvvLva())
        self.engine = AlphaBeta(self.eval_pipeline, self.sort_pipeline)

        # constants
        self.handlers = {
            "uci": self.uci,
            "isready": self.isready,
            "position": self.position,
            "go": self.go
        }

        # attributes
        self.board = chess.Board()
        self.move_stack: list[chess.Move] = []

    def read(self) -> str:
        command = sys.stdin.readline()
        return command.strip()

    def run(self) -> None:
        uci_input = None

        while True:
            uci_input = self.read().split()

            # check if command exists
            if len(uci_input) == 0 or uci_input[0] == "quit":
                logger.log("GUI closed connection")
                break

            command = uci_input[0]
            logger.log(" ".join(uci_input), logger.IN)

            if command in self.handlers:
                try:
                    self.handlers[command](*uci_input[1:])
                except Exception as error:
                    logger.log(f"Command error '{command}' with args {uci_input[1:]}", logger.WARNING)
                    logger.log(str(error), logger.WARNING)
            else:
                logger.log(f"Unknown command: '{command}'", logger.WARNING)
    
    def uci(self, *_) -> None:
        print("id name BiasFish")
        print("id author RealPhonki")
        print("uciok")
        logger.log("id name BiasFish", logger.OUT)
        logger.log("id author RealPhonki", logger.OUT)
        logger.log("uciok", logger.OUT)
        sys.stdout.flush()
    
    def isready(self, *_) -> None:
        print("readyok")
        logger.log("readyok", logger.OUT)
        sys.stdout.flush()
    
    def position(self, *args) -> None:
        head, body = args[0], list(args[1:])

        # load start position
        if head == "startpos":
            self.board.reset()
            logger.log("position set: startpos")
            while body and body[0] != "moves":
                body.pop(0)

        # load fen
        elif head == "fen":
            fen = []
            while body and body[0] != "moves":
                fen.append(body.pop(0))
            
            self.board.set_fen(" ".join(fen))
            logger.log("position set: " + " ".join(fen))

        else:
            raise CommandError()
        
        # load move stack
        if body and body[0] == "moves":
            body.pop(0)

            for move_uci in body:
                move = chess.Move.from_uci(move_uci)

                self.board.push(move)

            logger.log("moves set: " + ", ".join(body[1:]))
    
    def go(self, *args) -> None:
        head, body = args[0], args[1:]

        if head == "depth":
            depth = int(body[0])
        else:
            depth = 5
        
        best_move = self.engine.get_best_move(self.board, depth)
        print(f"bestmove {best_move}")
        logger.log(f"bestmove {best_move}")
        sys.stdout.flush()

if __name__ == "__main__":
    app = UCIHandler()
    app.run()