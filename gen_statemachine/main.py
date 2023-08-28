import logging
import argparse
import importlib
import inspect
from gen_statemachine import frontend, backend, model
from pathlib import Path
from sys import stdout
from typing import Callable, Tuple, List
from gen_statemachine.diag import Diagnostics, NullDiagnostics, LOG_FORMAT
from gen_statemachine.error import ProgramError
from gen_statemachine.model.model import StateMachine

LOGGER = logging.getLogger(__name__)


class Program:
    def __init__(self, enable_stdout_debug: Callable):
        self.parser = frontend.Parser()
        self.model_builder = model.ModelBuilder()
        self.target_generator = backend.TargetGenerator()
        self.diag = NullDiagnostics()
        self.enable_stdout_debug = enable_stdout_debug

    def parse_args(self) -> Tuple[argparse.Namespace, List[str]]:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "input_file",
            help="Path to file containing a PlantUML State Diagram",
            type=Path,
        )
        parser.add_argument(
            "output_dir",
            help="Directory to output generated files to",
            type=Path,
        )
        parser.add_argument(
            "--diag",
            action="store_true",
            dest="enable_diag",
            help="Save logs to output dir",
            default=False,
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            dest="enable_debug_logging",
            help="Print full logging output. This will slow down the program.",
            default=False,
        )
        parser.add_argument(
            "--target",
            dest="target_name",
            help="Name of target for code generation. Available targets: [`python3/native`]",
            type=str,
            default="python3/native",
        )
        parser.add_argument(
            "--generate-entrypoint",
            action="store_true",
            dest="generate_entrypoint",
            help="Generate entrypoint code (e.g. `main` file)",
            default=False,
        )
        return parser.parse_known_args()

    def run(self):

        try:
            args, _ = self.parse_args()

            if args.enable_debug_logging:
                self.enable_stdout_debug()
            LOGGER.debug(f"Parsed args: {args}")

            if args.enable_diag:
                self.diag = Diagnostics(args.output_dir / "logs")

            LOGGER.info("Generating parse tree..")
            parse_tree: frontend.ParseTree = None
            with open(args.input_file, "r") as file:
                parse_tree = self.parser.parse_puml(file)
            self.diag.save_text_file(str(parse_tree), "parse_tree.txt")

            LOGGER.info("Generating statemachine model..")
            statemachine: StateMachine = self.model_builder.build(parse_tree)

            LOGGER.info("Generating statemachine code..")
            args.output_dir.mkdir(parents=True, exist_ok=True)
            self.target_generator.generate(
                args.target_name, args.output_dir, statemachine
            )

            LOGGER.info("Done!")
        except ProgramError as e:
            LOGGER.error(e)
        except Exception as e:
            program_error = ProgramError(f"{e}")
            LOGGER.exception(program_error)


def main():
    # The root logger is configured for full verbosity here so
    # that any attached logging handlers can configure the
    # desired verbosity themselves
    logging.getLogger().setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(stream=stdout)
    stream_handler.setLevel(level=logging.INFO)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger().addHandler(stream_handler)

    program = Program(
        enable_stdout_debug=lambda: stream_handler.setLevel(logging.DEBUG)
    )
    program.run()


if __name__ == "__main__":
    main()
