import os
import logging
from pathlib import Path
from sys import stdout

import frontend

LOGGER = logging.getLogger(__name__)


class Program:
    def __init__(self):
        self.parser = frontend.Parser()

    def run(self):
        # TODO: Parse args
        file_path = Path(os.getcwd()) / "examples" / "full_syntax.puml"

        with open(file_path, "r") as file:
            try:
                parse_tree = self.parser.parse_puml(file)
            except frontend.ParseError as e:
                LOGGER.exception(e)

        LOGGER.debug(f"Generated parse tree:\n{parse_tree}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=stdout)
    program = Program()
    program.run()
