import logging
import re
from typing import Optional, TextIO, List, Tuple, Match

from gen_fsm.frontend.tokens import Token, TokenType, patterns

LOGGER = logging.getLogger(__name__)


class FilePosition:
    def __init__(self, line_no: int = 1, column_no: int = 0):
        assert line_no >= 1
        assert column_no >= 0
        self.line_no = line_no
        self.column_no = column_no


class FileReader:
    """
    Provides an interface to read or peek at characters from a file.
    Although we could read files 1 character at a time, this implementation
    just reads the full file into memory as they are expected to be small.
    """

    def __init__(self, file: TextIO):
        self.file = file
        self.read_position = FilePosition(1, 0)
        self.lines = file.readlines()

    def read_next(self) -> str:
        """Returns the next char in the file, and increments the read position"""
        if self.end_of_file():
            return ""

        char, position = self._get_next_char()
        self.read_position = position
        return char

    def peek_next(self) -> str:
        """Returns the next char in the file without incrementing the read position"""
        if self.end_of_file():
            return ""

        char, _ = self._get_next_char()
        return char

    def end_of_file(self) -> bool:
        """Returns `True` if the end of file has been reached"""
        return self.read_position.line_no > len(self.lines)

    def _get_next_char(self) -> Tuple[str, FilePosition]:
        """Returns next char from read position, or empty string if EOF is reached"""
        current_line = self.lines[self.read_position.line_no - 1]
        next_position = FilePosition(
            self.read_position.line_no, self.read_position.column_no + 1
        )
        if next_position.column_no > len(current_line):
            next_position.column_no = 1
            next_position.line_no += 1

        return self._get_char_at_position(next_position), next_position

    def _get_char_at_position(self, position: FilePosition) -> str:
        """Returns char at given position or empty string if the position is out of range"""
        if position.line_no > len(self.lines):
            return ""

        if position.column_no > len(self.lines[position.line_no - 1]):
            return ""

        return self.lines[position.line_no - 1][position.column_no - 1]


class Lexer:
    """
    Responsible for tokenizing the input file, by matching sub-strings from the file
    against known token patterns. The Parser tells the Lexer what to look for based
    on the rules of the language and the previously identified tokens.
    """

    def __init__(self, file: TextIO):
        self.file_reader = FileReader(file)
        self.compiled_patterns = {}
        for token_type, pattern in patterns.items():
            self.compiled_patterns[token_type] = re.compile(pattern)

    def look_for_tokens(
        self, take: List[TokenType], skip: List[TokenType] = []
    ) -> Token:
        """
        Attempts to scan the file for the first token that is in the `take` list and not
        in the `skip` list. If no tokens from the `take` list are found, then an EOF token
        is returned (because we looked up until the end)
        """
        # Combine take and skip to find both types, tokens
        # in the skip list will simply be discarded once found
        expected_tokens = take + skip
        while True:
            token = self._find_next(expected_tokens)

            if token.type in skip:
                LOGGER.debug(f"Skipping {token}")
                continue
            else:
                LOGGER.debug(f"Found {token}")
                return token

    def _find_next(self, token_types: List[TokenType]) -> Token:
        """
        Iterates through the file 1 character at a time to find a
        string that matches one of the expected token patterns. Once
        a string is found that matches a token, we attempt to expand
        that string to find the maximum set of characters that still
        match the token.
        """
        curent_token = Token(
            start_line=self.file_reader.read_position.line_no,
            start_col=self.file_reader.read_position.column_no + 1,
        )
        # Look for the start of a token
        while curent_token.type is TokenType.UNKNOWN:
            next_char = self.file_reader.read_next()
            if next_char == "":
                curent_token.type = TokenType.EOF
            else:
                curent_token.text += next_char
                curent_token.type = self._id_token_from_text(
                    curent_token.text, token_types
                )

        # Now look for the end of the token
        end_of_token_found = False
        while not end_of_token_found:
            if curent_token.type is TokenType.EOF:
                return curent_token

            next_token_type = self._look_ahead_for_token(curent_token.text, token_types)
            token_type_changed = curent_token.type is not next_token_type

            if token_type_changed:
                changed_to_superseding_type = (
                    next_token_type in token_types
                    and token_types.index(next_token_type)
                    < token_types.index(curent_token.type)
                )
                if not changed_to_superseding_type:
                    end_of_token_found = True

            if not end_of_token_found:
                curent_token.text += self.file_reader.read_next()
                curent_token.type = next_token_type

        return curent_token

    def _look_ahead_for_token(
        self, token_text: str, token_types: List[TokenType]
    ) -> TokenType:
        """
        Using the current text sequence and the next character in file,
        identifies and returns the first matching token type, or UNKNOWN
        if there are no matches, or EOF if there is no next character in
        the file.
        """
        next_char = self.file_reader.peek_next()

        if next_char == "":
            return TokenType.EOF

        next_text = token_text + next_char
        return self._id_token_from_text(next_text, token_types)

    def _id_token_from_text(self, text: str, token_types: List[TokenType]):
        """Returns the *first* token in `token_types` whose pattern matches
        the given text, or UNKNOWN if no match is found"""
        for token in token_types:
            if self._text_matches_token_pattern(token, text):
                return token
        return TokenType.UNKNOWN

    def _text_matches_token_pattern(
        self, token: TokenType, text: str
    ) -> Optional[Match[str]]:
        """Returns `True` if the text wholly matches the pattern for this token type"""
        if token in self.compiled_patterns:
            return self.compiled_patterns[token].match(text)
        else:
            raise RuntimeError(f"No pattern stored for {token} token type")
