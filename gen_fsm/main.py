import logging
import argparse
import importlib
from gen_fsm import frontend
from gen_fsm import model
from pathlib import Path
from sys import stdout
from typing import Tuple, List

LOGGER = logging.getLogger(__name__)


class Program:
    def __init__(self):
        self.parser = frontend.Parser()
        self.model_builder = model.ModelBuilder()

    def parse_args(self) -> Tuple[argparse.Namespace, List[str]]:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "input_file",
            help="Path to file containing a PlantUML State Diagram",
            type=Path,
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
                LOGGER.debug(f"Generated parse tree:\n{parse_tree}")

                LOGGER.info("Generating statemachine model..")
                statemachine_model = self.model_builder.build(parse_tree)

                LOGGER.info("Invoking codegen module..")
                codegen_module.generate_statemachine_code(
                    statemachine_model, plugin_args
                )

            except frontend.ParseError as e:
                LOGGER.exception(e)
            except Exception as e:
                LOGGER.exception(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=stdout)
    program = Program()
    program.run()
