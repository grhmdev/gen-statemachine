from pathlib import Path
from datetime import datetime
import os
import logging

LOGGER = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s: %(message)s"


class NullDiagnostics:
    """
    Null implementation of the Diagnostics interface, used to
    optionally disable diag functionality
    """

    def save_text_file(self, contents: str, file_name: str):
        pass


class Diagnostics:
    """
    Responsible for writing diagnostic info (logs and other artifacts)
    to file. These files will be output to a timestamped directory
    generated for each run.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.output_dir.mkdir(parents=True, exist_ok=False)
        latest_dir = output_dir / "latest"
        if os.path.islink(latest_dir):
            latest_dir.unlink()
        latest_dir.symlink_to(self.output_dir.resolve(), target_is_directory=True)
        self._init_log_file()

    def _init_log_file(self):
        """
        Configures the root logger to also send log messages
        to a file, with full verbosity.
        """
        self.log_file = self.output_dir / "log.txt"
        file_handler = logging.FileHandler(filename=self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger().addHandler(file_handler)
        LOGGER.info(f"Logging to {self.log_file}")

    def save_text_file(self, contents: str, file_name: str):
        path = self.output_dir / file_name
        LOGGER.info(f"Writing file: {path}")
        path.write_text(contents)
