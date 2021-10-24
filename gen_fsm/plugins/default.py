import logging
import argparse
from pathlib import Path
from gen_fsm.model import StateMachine
from typing import List

# Mako rendering
from mako.template import Template
from mako.lookup import TemplateLookup
from mako.runtime import Context
from mako import exceptions
from io import StringIO

LOGGER = logging.getLogger(__name__)


def generate_statemachine_code(
    statemachine_model: StateMachine, output_dir: Path, args: List[str]
):
    codegen = CodegenPlugin(statemachine_model, output_dir, args)
    codegen.run()


class CodegenPlugin:
    def __init__(
        self, statemachine_model: StateMachine, output_dir: Path, raw_args: List[str]
    ):
        self.output_dir = output_dir
        self.args = self.parse_args(raw_args)
        self.mako_renderer = MakoRenderer(self.args.template_dir, statemachine_model)

    def parse_args(self, args: List[str]) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--templates",
            dest="template_dir",
            help="Directory containing template files and other resources",
            type=Path,
            default=Path.cwd() / "gen_fsm/plugin_resources/python3/templates",
        )
        return parser.parse_args(args)

    def run(self):
        LOGGER.info("Generating statemachine code..")
        LOGGER.info(f"--templates {self.args.template_dir}")

        # Check the arguments are valid
        if not self.args.template_dir.exists():
            raise RuntimeError(
                f"Template directory does not exist: {self.args.template_dir}"
            )

        # Create the output directory if it does not yet exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Begin iterating through template files
        self.process_dir(self.args.template_dir)

        LOGGER.info("Generation done")

    def process_dir(self, dir: Path):
        """Recursively finds files in the directory and processes them. The files in the directory are processed first, before any sub-directories."""
        files = []
        dirs = []
        for child in dir.iterdir():
            if child.is_file():
                files.append(child)
            elif child.is_dir():
                dirs.append(child)
            else:
                LOGGER.warn(f"Unexpected item in directory: {child.name}")

        # First process identified files
        for file in files:
            self.process_file(file)

        # Find files in nested directories
        for dir in dirs:
            self.process_dir(dir)

    def process_file(self, file_path: Path):
        """If this file is a template, render it otherwise just simply copy the file to the output."""
        if file_path.suffix in [".mako"]:
            LOGGER.info(f"Rendering mako template: {file_path.name}")
            text = self.mako_renderer.render_template(file_path.read_text())
            output_file = self.get_output_path(file_path)
            output_file = output_file.with_name(output_file.name.replace(".mako", ""))
            output_file.parents[0].mkdir(parents=True, exist_ok=True)
            LOGGER.info(f"Writing file: {output_file}")
            output_file.write_text(text)
        else:
            output_file = self.get_output_path(file_path)
            LOGGER.info(f"Copying file to output: {output_file}")
            output_file.parents[0].mkdir(parents=True, exist_ok=True)
            output_file.write_bytes(file_path.read_bytes())

    def get_output_path(self, input_path: Path) -> Path:
        """Creates output path for a file, preserving the relative path from the input directory."""
        relative_path = input_path.relative_to(self.args.template_dir)
        return self.output_dir / relative_path


class MakoRenderer:
    def __init__(self, template_dir: Path, statemachine_model: StateMachine):
        self.template_lookup = TemplateLookup(directories=[template_dir])
        self.statemachine = statemachine_model

    def render_template(self, template_str: str) -> str:
        buffer = StringIO()
        context = Context(buffer, statemachine=self.statemachine)
        template = Template(template_str, lookup=self.template_lookup)
        try:
            template.render_context(context)
        except Exception as e:
            LOGGER.error(exceptions.text_error_template().render())
            raise e

        return buffer.getvalue()
