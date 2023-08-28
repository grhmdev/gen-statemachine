from pathlib import Path
import gen_statemachine.main
import shutil
import importlib.util
import io
from contextlib import redirect_stdout
import sys
import logging
from unittest.mock import Mock, call
from tests.utilities import TestCaseBase
from typing import List


class EndToEndTestCase(TestCaseBase):
    def setUp(self):
        super().setUp()
        test_name = self.__class__.__name__
        self.test_spec = (
            Path(__file__).parent.absolute() / "tests" / (test_name + ".test")
        )
        # Remove and re-create test output dir
        self.output_dir = Path(__file__).parent.absolute() / "results" / test_name
        shutil.rmtree(self.output_dir, ignore_errors=True)
        self.output_dir.mkdir(parents=True)

        self.log_file = self.output_dir / "test.log"
        logging.basicConfig(filename=self.log_file, filemode="w", level=logging.DEBUG)

    def run_gen_statemachine(self):
        # Set program args & logging config
        sys.argv = [__name__, str(self.test_spec), str(self.output_dir), "--diag"]
        # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

        program = gen_statemachine.main.Program(enable_stdout_debug=lambda: None)
        program.run()

    def read_expected_output(self) -> List[str]:
        file_content = self.test_spec.read_text()
        start_tag = "@startexpected"
        end_tag = "@endexpected"
        start_tag_index = file_content.find(start_tag)
        end_tag_index = file_content.find(end_tag)
        expected_output = file_content[start_tag_index + len(start_tag) : end_tag_index]
        return [line for line in expected_output.split("\n") if line.strip() != ""]

    def import_statemachine_module(self):
        sys.path.append(str(self.output_dir))
        spec = importlib.util.spec_from_file_location(
            "statemachine", self.output_dir / "statemachine.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run_statemachine(self) -> List[str]:
        module = self.import_statemachine_module()
        sm = module.StateMachine()
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            sm.start()
        return [line for line in stdout.getvalue().split("\n") if line.strip() != ""]

    def run_test(self):
        expected_output = self.read_expected_output()

        self.run_gen_statemachine()
        output = self.run_statemachine()

        self.assertEqual(output, expected_output)
