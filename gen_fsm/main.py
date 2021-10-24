import logging
import argparse
import importlib
from gen_fsm import frontend
from gen_fsm import model
from pathlib import Path
from sys import stdout
from typing import Callable, Tuple, List
import diag

LOGGER = logging.getLogger(__name__)


class Program:
    def __init__(self, enable_stdout_debug: Callable):
        self.parser = frontend.Parser()
        self.model_builder = model.ModelBuilder()
        self.diag = diag.NullDiagnostics()
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
            "--codegen-module",
            dest="codegen_module_name",
            help="Python module to import for statemachine code generation",
            type=str,
            default="gen_fsm.plugins.default",
        )
        return parser.parse_known_args()

    def run(self):
        args, plugin_args = self.parse_args()

        if args.enable_debug_logging:
            self.enable_stdout_debug()

        if args.enable_diag:
            self.diag = diag.Diagnostics(args.output_dir / "logs")

        try:
            codegen_module = importlib.import_module(args.codegen_module_name)
            LOGGER.info(f"Found codegen module: {args.codegen_module_name}")
        except ModuleNotFoundError as e:
            LOGGER.error(f"Failed to import codegen module: {args.codegen_module_name}")
            LOGGER.exception(e)
            exit()

        with open(args.input_file, "r") as file:
            try:
                LOGGER.info("Generating parse tree..")
                parse_tree = self.parser.parse_puml(file)
                self.diag.save_text_file(str(parse_tree), "parse_tree.txt")

                LOGGER.info("Generating statemachine model..")
                statemachine_model = self.model_builder.build(parse_tree)

                LOGGER.info("Invoking codegen module..")
                codegen_module.generate_statemachine_code(
                    statemachine_model, args.output_dir, plugin_args
                )

            except frontend.ParseError as e:
                LOGGER.exception(e)
            except Exception as e:
                LOGGER.exception(e)


def main():
    # The root logger is configured for full verbosity here so
    # that any attached logging handlers can configure the
    # desired verbosity themselves
    logging.getLogger().setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(stream=stdout)
    stream_handler.setLevel(level=logging.INFO)
    stream_handler.setFormatter(logging.Formatter(diag.LOG_FORMAT))
    logging.getLogger().addHandler(stream_handler)

    program = Program(
        enable_stdout_debug=lambda: stream_handler.setLevel(logging.DEBUG)
    )
    program.run()


if __name__ == "__main__":
    main()
