from typing import Any
import unittest
import os
from pathlib import Path


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        self.test_file_dir = Path(__file__).parent / ".temp"
        self.test_file_dir.mkdir(exist_ok=True)
        self.test_files = []

    def tearDown(self):
        # Remove any files created
        for file in self.test_files:
            file.unlink()
        self.test_file_dir.rmdir()

    def create_file(self, name: str = "test.file", contents: str = "") -> Path:
        path = Path(os.getcwd()) / ".temp" / name
        path.write_text(contents)
        self.test_files.append(path)
        return path
