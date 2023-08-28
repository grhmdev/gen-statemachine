import unittest
from tests.utilities import TestCaseBase

from gen_statemachine.frontend.lexer import FileReader


class TestFileReader(TestCaseBase):
    def test_empty_file(self):
        file_path = self.create_file(contents="")
        with open(file_path, "r") as file:
            uut = FileReader(file)
            self.assertEqual(uut.read_next(), "")
            self.assertEqual(uut.peek_next(), "")

    def test_read_next(self):
        file_path = self.create_file(contents="A\nB")
        with open(file_path, "r") as file:
            uut = FileReader(file)
            # Read 'A'
            self.assertEqual(uut.read_next(), "A")
            self.assertEqual(uut.read_position.line_no, 1)
            self.assertEqual(uut.read_position.column_no, 1)
            # Read newline
            self.assertEqual(uut.read_next(), "\n")
            self.assertEqual(uut.read_position.line_no, 1)
            self.assertEqual(uut.read_position.column_no, 2)
            # Read 'B'
            self.assertEqual(uut.read_next(), "B")
            self.assertEqual(uut.read_position.line_no, 2)
            self.assertEqual(uut.read_position.column_no, 1)
            # Read EOF
            self.assertEqual(uut.read_next(), "")

    def test_peek_next(self):
        file_path = self.create_file(contents="AB")
        with open(file_path, "r") as file:
            uut = FileReader(file)
            self.assertEqual(uut.peek_next(), "A")
            self.assertEqual(uut.read_next(), "A")
            self.assertEqual(uut.peek_next(), "B")
            self.assertEqual(uut.peek_next(), "B")
            self.assertEqual(uut.read_next(), "B")
            self.assertEqual(uut.peek_next(), "")


if __name__ == "__main__":
    unittest.main()
