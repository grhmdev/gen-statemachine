import logging
from gen_statemachine import frontend, backend, model
from typing import Callable
from gen_statemachine.diag import Diagnostics, NullDiagnostics
from gen_statemachine.error import ProgramError
from gen_statemachine.model import StateMachine
from gen_statemachine.parse_args import parse_args

LOGGER = logging.getLogger(__name__)


class Program:
    """
    Responsible for the high level execution of the program,
    and catching any emitted errors
    """

    def __init__(self, enable_stdout_debug: Callable):
        self.parser = frontend.Parser()
        self.model_builder = model.ModelBuilder()
        self.target_generator = backend.TargetGenerator()
        self.diag = NullDiagnostics()
        self.enable_stdout_debug = enable_stdout_debug

    def run(self):
        try:
            args, _ = parse_args()

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
