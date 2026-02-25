# standard
from datetime import datetime
import pathlib

class Logger:
    """ Handles all logging """
    IN      = "GUI << "
    OUT     = "ENG >> "
    INFO    = "INFO - "
    WARNING = "WARNING - "
    ERROR   = "ERROR - "
    def __init__(self) -> None:
        self.path = pathlib.Path(self.make_path())

        self.make_dir()

    def make_path(self) -> str:
        """ Constructs a path for the current year and month.

        Returns:
            str: The output path.
        """
        date = datetime.now()
        month = date.strftime("%B")
        return f"logs/{date.year}/{month}"

    def make_dir(self) -> None:
        """ If the path generated does not exist, then create one. """
        if not self.path.exists():
            self.path.mkdir(parents=True)
    
    def log(self, text: str, direction = "INFO - ") -> None:
        """ Writes a message to the log file for the current time

        Args:
            text (str): The message to write to the log file
            direction (str, optional): The source of the message. Defaults to "INFO".
        """
        with open(self.path / f"{datetime.now().day}.log", "a", encoding="UTF-8") as file:
            file.write(str(datetime.now().time()) + " - " + direction + text + "\n")

logger = Logger()