import argparse
from typing import Tuple, List
from pathlib import Path


def parse_args() -> Tuple[argparse.Namespace, List[str]]:
    """
    Parses command line arguments used by gen_statemachine
    """
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
