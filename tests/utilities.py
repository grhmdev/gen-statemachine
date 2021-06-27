from typing import Any
import unittest
import os
from pathlib import Path


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.test_file_paths = []

    def tearDown(self):
        # Remove any files created
        for path in self.test_file_paths:
            path.unlink()

    def create_file(self, name: str = "test.file", contents: str = "") -> Path:
        path = Path(os.getcwd()) / ".temp" / name
        path.write_text(contents)
        self.test_file_paths.append(path)
        return path
