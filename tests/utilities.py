from typing import Any
import unittest
import os
from pathlib import Path


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.test_file_paths = []

    def tearDown(self):
        # Remove any files created
        map(lambda x: x.unlink(), self.test_file_paths)

    def create_file(self, name: str = "test.file", contents: str = "") -> Path:
        path = Path(os.getcwd()) / name
        path.write_text(contents)
        self.test_file_paths.append(path)
        return path
