"""
A 'target' is a language and/or implementation to generate statemachine code
for. The target directory should contain a manifest file which lists the files
contained within the directory and their types.

The TargetGenerator is therefore responsible for processing target files that
are listed by the manifest and performing actions depending on the file types.
"""

import logging
from pathlib import Path
from gen_statemachine.error import ProgramError
from gen_statemachine.model import StateMachine

from gen_statemachine.backend.manifest import (
    TargetFile,
    load_target_manifest,
)
from gen_statemachine.backend.mako_renderer import MakoRenderer


LOGGER = logging.getLogger(__name__)


class TargetGenerator:
    """Generates output files (typically code) for targets"""

    def __init__(self):
        self.targets_dir = Path(__file__).parent / "targets"
        self.generate_entrypoints = True

    def generate(self, target_name: str, output_dir: Path, statemachine: StateMachine):
        """
        Attempts to read a manifest file from the directory named `target_name`
        and then sequentially processes all other files in the directory that
        are listed in the manifest.
        """
        target_dir = self.targets_dir / target_name
        target_dir = target_dir.resolve()

        if not target_dir.exists():
            raise ProgramError(f"Target {target_name} not found in {self.targets_dir}")

        self.mako_renderer = MakoRenderer(target_dir, statemachine)
        manifest = load_target_manifest(target_dir)
        LOGGER.info(f"Loaded {manifest.target} manifest")

        for _, file in manifest.files.items():
            self._process_file(file, target_dir, output_dir, statemachine)

    def _process_file(
        self,
        file: TargetFile,
        target_dir: Path,
        output_dir: Path,
        statemachine: StateMachine,
    ):
        """
        Depending on the type of the TargetFile, performs actions:
        - For a template file, the template is rendered and text output to a
          file in the output directory
        - For a source code file, the file is simply copied into the output dir
          without alteration
        - For an entrypoint file, the file is optionally copied into the output
          dir (the same as a source file)
        """

        file_path = target_dir / file.path
        if not file_path.exists():
            raise ProgramError(f"The file {file.path} does not exist! ({file_path})")

        if file.is_mako_template_file():
            output_path = output_dir / file.destination
            self._create_directories(output_path)
            self._render_mako_template(file_path, output_path, statemachine)
        elif file.is_entrypoint_file() and not self.generate_entrypoints:
            LOGGER.info(f"Skipping entrypoint file: {file.path}")
        elif file.is_source_file() or file.is_entrypoint_file():
            # Copy from source to destination
            output_path = output_dir / file.destination
            LOGGER.info(f"Generating {output_path}")
            self._create_directories(output_path)
            output_path.write_text(file_path.read_text())
        else:
            LOGGER.warn(f"Unexpected file in target manifest: {file.path}")

    def _create_directories(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)

    def _render_mako_template(
        self, template_path: Path, output_path: Path, statemachine: StateMachine
    ):
        LOGGER.info(f"Generating {output_path}")
        text = self.mako_renderer.render_template(template_path.read_text())
        output_path.write_text(text)
