# pylint: disable=broad-exception-caught

# standard
import threading
import sys

# third party
import chess

# project
from biasfish.search.move_ordering import MoveOrdering
from biasfish.search.evaluation import Evaluation
from biasfish.search.engine import Engine

from biasfish.debug.logger import logger

class CommandError(Exception):
    """
    This exception is raised when the UCI Handler processes
    an unrecognized command.
    """

class UCIHandler:
    """
    This class handles all uci commands and sends them to the engine.
    """
    def __init__(self) -> None:
        # subclasses
        self.engine = Engine(Evaluation(), MoveOrdering())

        # constants
        self.handlers = {
            "uci": self.uci,
            "isready": self.isready,
            "position": self.position,
            "go": self.go,
            "stop": self.stop,
            "quit": self.quit
        }

        # attributes
        self.board = chess.Board()
        self.move_stack: list[chess.Move] = []
        self.search_thread = None

    def read(self) -> str:
        """ Reads the input, strips whitespaces, and returns it

        Returns:
            str: Represents the stripped input.
        """
        raw_input = sys.stdin.readline()

        # check for EOF
        if raw_input == "":
            logger.log("GUI closed connection")
            self.quit()

        return raw_input.strip().split()

    def run(self) -> None:
        """
        Starts an infinite loop and listens for commands.
        When commands are entered they are indexed with the handler hashmap
        and the command is executed if it exists.
        """

        uci_input = None

        while True:
            uci_input = self.read()

            # ignore empty lines
            if len(uci_input) == 0:
                continue

            command = uci_input[0]
            uci_input.pop(0)
            logger.log(f"{command} " + " ".join(uci_input), logger.IN)

            if command in self.handlers:
                try:
                    self.handlers[command](*uci_input)
                except Exception as error:
                    logger.log(f"Command error '{command}' with args {uci_input}", logger.WARNING)
                    logger.log(str(error), logger.WARNING)
            else:
                logger.log(f"Unknown command: '{command}'", logger.WARNING)
    
    def uci(self, *_) -> None:
        """
        Handles the UCI command
        """
        print("id name BiasFish")
        print("id author RealPhonki")
        print("uciok")
        logger.log("id name BiasFish", logger.OUT)
        logger.log("id author RealPhonki", logger.OUT)
        logger.log("uciok", logger.OUT)
        sys.stdout.flush()
    
    def isready(self, *_) -> None:
        """
        Handles the isready command
        """
        print("readyok")
        logger.log("readyok", logger.OUT)
        sys.stdout.flush()
    
    def position(self, *args) -> None:
        """
        Handles the position command. This command sets the board state and
        loads the move stack if specified.

        Raises:
            CommandError: Represents the exception raised when unknown arguments are passed
        """
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

            logger.log("moves set: " + ", ".join(body))
    
    def go(self, *args) -> None:
        """
        Handles the go command.
        This method starts a new thread and instructs the engine to search using that thread.

        Raises:
            CommandError: Represents the exception raised when unknown arguments are passed.
        """
        head, body = args[0], args[1:]

        if head == "depth":
            depth = int(body[0])
        else:
            raise CommandError()
        
        self.search_thread = threading.Thread(target=self._search, args=[depth])
        self.search_thread.start()
    
    def _search(self, depth: int) -> None:
        best_move = self.engine.get_best_move(self.board, depth)
        print(f"bestmove {best_move}")
        logger.log(f"bestmove {best_move}")
        sys.stdout.flush()

    def stop(self, *_) -> None:
        """
        Handles the stop command. 
        This method kills the engine's search thread if it exists.
        """
        if self.search_thread and self.search_thread.is_alive():
            logger.log("Aborting search...")

            self.engine.search_ctx.stop_flag = True
            self.search_thread.join() # wait until the thread terminates
    
    def quit(self) -> None:
        """
        Closes the log file and kills the engine before terminating the script
        """
        self.stop()
        logger.log("Quiting...")
        logger.close()
        sys.exit(0)

def main():
    app = UCIHandler()
    app.run()

if __name__ == "__main__":
    main()