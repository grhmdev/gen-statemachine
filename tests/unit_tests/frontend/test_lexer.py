from gen_fsm.frontend.tokens import Token, TokenType
from typing import List
import unittest
from tests.utilities import TestCaseBase

from gen_fsm.frontend.lexer import Lexer


class TestLexer(TestCaseBase):
    def look_for_token(
        self,
        file_contents: str,
        tokens_to_find: List[TokenType],
        tokens_to_skip: List[TokenType],
        expected_result: Token,
    ):
        file_path = self.create_file(contents=file_contents)
        with open(file_path, "r") as file:
            uut = Lexer(file)
            token = uut.look_for_tokens(tokens_to_find, tokens_to_skip)
            self.assertEqual(token.type, expected_result.type)
            self.assertEqual(token.text, expected_result.text)
            self.assertEqual(token.start_line, expected_result.start_line)
            self.assertEqual(token.start_col, expected_result.start_col)

    def test_token_not_found(self):
        """Test EOF token is returned at end of file"""
        self.look_for_token(
            file_contents="\n@startuml",
            tokens_to_find=[TokenType.KEYWORD_START_UML],
            tokens_to_skip=[],
            expected_result=Token(TokenType.EOF, 1, 1, "\n@startuml"),
        )

    def test_token_not_found_with_skip(self):
        """Test EOF token is returned at end of file"""
        self.look_for_token(
            file_contents=" ",
            tokens_to_find=[TokenType.KEYWORD_START_UML],
            tokens_to_skip=[TokenType.WHITESPACE],
            expected_result=Token(TokenType.EOF, 1, 2, ""),
        )

    def test_token_found(self):
        """Test token identification without other characters"""
        token_text = "@startuml"
        self.look_for_token(
            file_contents=token_text,
            tokens_to_find=[TokenType.KEYWORD_START_UML],
            tokens_to_skip=[],
            expected_result=Token(TokenType.KEYWORD_START_UML, 1, 1, token_text),
        )

    def test_token_found_with_skip(self):
        """Test token identification with leading characters to skip"""
        token_text = "@startuml"
        self.look_for_token(
            file_contents=f"      {token_text}",
            tokens_to_find=[TokenType.KEYWORD_START_UML],
            tokens_to_skip=[TokenType.WHITESPACE],
            expected_result=Token(TokenType.KEYWORD_START_UML, 1, 7, token_text),
        )

    def test_token_precedence(self):
        """Test token identification with 2 possible candidates"""
        token_text = "state"
        self.look_for_token(
            file_contents=f"{token_text}",
            tokens_to_find=[TokenType.KEYWORD_STATE, TokenType.NAME],
            tokens_to_skip=[],
            expected_result=Token(TokenType.KEYWORD_STATE, 1, 1, token_text),
        )


if __name__ == "__main__":
    unittest.main()
