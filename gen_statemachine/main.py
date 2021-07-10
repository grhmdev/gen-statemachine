import logging
import argparse
from pathlib import Path
from sys import stdout

import frontend

LOGGER = logging.getLogger(__name__)


class Program:
    def __init__(self):
        self.parser = frontend.Parser()

    def parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "input_file",
            help="Path to file containing a PlantUML State Diagram",
            type=Path,
        )
        return parser.parse_args()

    def run(self):
        args = self.parse_args()
        with open(args.input_file, "r") as file:
            try:
                parse_tree = self.parser.parse_puml(file)
            except frontend.ParseError as e:
                LOGGER.exception(e)

        LOGGER.debug(f"Generated parse tree:\n{parse_tree}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=stdout)
    program = Program()
    program.run()
