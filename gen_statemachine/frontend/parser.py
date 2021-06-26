from copy import deepcopy
from typing import TextIO, List, Callable, NewType, Optional

from .lexer import LOGGER, Lexer
from .tokens import Token, TokenType


class Node:
    def __init__(self, token: Token):
        self.token = token
        self.children: List[Node] = []
        self.parent: Optional[Node] = None

    def make_child(self, token: Token) -> "Node":
        assert type(token) is Token
        n = Node(token)
        self.children.append(n)
        n.parent = self
        return n

    def to_str(self, depth=0):
        s = ("  " * depth) + "└ "
        if self.token:
            s += f"<{self.token.type}>: " + self.token.text.replace("\n", "\\n")
        else:
            s += "root"

        for child in self.children:
            s += "\n" + child.to_str(depth + 1)
        return s


class ParseTree:
    def __init__(self):
        self.root_node = Node(None)

    def __str__(self):
        return self.root_node.to_str(0)


class ParseError(RuntimeError):
    def __init__(self, error_message: str, file_name=None, line_no=0, column_no=0):
        self.file_name = file_name
        self.line_no = line_no
        self.column_no = column_no
        self.message = error_message

    def __str__(self):
        return f"""
        =======================================
        ʘ︵ʘ oh no!!!
        Parse error @ [{self.file_name}:{self.line_no}:{self.column_no}]
          {self.message}
        =======================================
        """


class Parser:
    """
    This parser is responsible for creating "setences" out of the "words" found by the
    lexer. It drives the parser by telling it exactly what to look for, and what to discard.
    If a word token is found that doesn't match the current sentence being parsed, then a
    `ParseError` is raised.
    """

    def __init__(self):
        self.root_node = Node(None)
        self.lexer = None
        self.parse_tree = ParseTree()

    def parse_puml(self, file: TextIO) -> ParseTree:
        self.lexer = Lexer(file)
        self.file_name = file.name

        # Find @startuml to begin parsing
        start_token = self.find_tokens(
            tokens_to_find=[TokenType.KEYWORD_START_UML],
            tokens_to_skip=[TokenType.WHITESPACE, TokenType.NEWLINE],
        )
        self.parse_tree.root_node.make_child(start_token)

        # Now parse following lines until @enduml is found
        end_token_found = False
        while end_token_found is False:
            # The order of tokens to search for is important here,
            # otherwise we'd falsely identify "state" as an identifier/name
            # rather than a keyword!
            token = self.lexer.look_for_tokens(
                skip=[TokenType.WHITESPACE, TokenType.NEWLINE],
                take=[
                    TokenType.KEYWORD_END_UML,
                    TokenType.KEYWORD_STATE,
                    TokenType.KEYWORD_NOTE,
                    TokenType.INITIAL_FINAL_STATE,
                    TokenType.NAME,
                ],
            )

            if token.type is TokenType.UNKNOWN:
                LOGGER.error(f"Unknown token found: {token}")
                break
            elif token.type is TokenType.EOF:
                LOGGER.warning("End-of-file found before closing @enduml")
                break
            elif token.type is TokenType.KEYWORD_END_UML:
                self.parse_tree.root_node.make_child(token)
                end_token_found = True
            elif token.type is TokenType.KEYWORD_STATE:
                self.parse_state_declaration(self.parse_tree.root_node, token)
            elif token.type is TokenType.KEYWORD_NOTE:
                self.parse_note_declaration(self.parse_tree.root_node, token)
            elif token.type in [TokenType.INITIAL_FINAL_STATE, TokenType.NAME]:
                self.parse_state_transition(self.parse_tree.root_node, token)

        return self.parse_tree

    def find_tokens(
        self, tokens_to_find: List[TokenType], tokens_to_skip: List[TokenType]
    ):
        next_token = self.lexer.look_for_tokens(tokens_to_find, tokens_to_skip)

        if next_token.type not in tokens_to_find:
            error_msg = """Unexpected symbols -> '{}'
             Expected one of -> {}""".format(
                next_token.text[: next_token.text.find("\n")],
                [str(t) for t in tokens_to_find],
            )
            raise ParseError(
                error_msg,
                self.file_name,
                next_token.start_line,
                next_token.start_col,
            )

        return next_token

    def parse_state_declaration(self, parent_node, first_token):
        LOGGER.debug("start of state_declaration")

        # Create node for production rule
        state_token = Token(
            type=TokenType.state_declaration, start_line=first_token.start_line
        )
        state_node = parent_node.make_child(state_token)

        # Add the 'state' token
        state_node.make_child(first_token)

        # Look for state name, or quotation enclosed label
        next_token = self.find_tokens(
            tokens_to_find=[TokenType.NAME, TokenType.QUOTATION],
            tokens_to_skip=[TokenType.WHITESPACE],
        )

        if next_token.type is TokenType.QUOTATION:
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.LABEL], tokens_to_skip=[TokenType.WHITESPACE]
            )
            state_node.make_child(next_token)

            next_token = self.find_tokens(
                tokens_to_find=[TokenType.QUOTATION],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

            next_token = self.find_tokens(
                tokens_to_find=[TokenType.KEYWORD_AS],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            state_node.make_child(next_token)

            next_token = self.find_tokens(
                tokens_to_find=[TokenType.NAME], tokens_to_skip=[TokenType.WHITESPACE]
            )
            state_node.make_child(next_token)

            next_token = self.find_tokens(
                tokens_to_find=[TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
        else:
            state_node.make_child(next_token)
            # Look for {, or newline
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.OPEN_CURLY_BRACKET, TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

            if next_token.type is TokenType.OPEN_CURLY_BRACKET:
                # Look for nested state declarations and state transitions
                while True:
                    next_token = self.find_tokens(
                        tokens_to_find=[
                            TokenType.KEYWORD_STATE,
                            TokenType.INITIAL_FINAL_STATE,
                            TokenType.NAME,
                            TokenType.CLOSE_CURLY_BRACKET,
                        ],
                        tokens_to_skip=[TokenType.WHITESPACE, TokenType.NEWLINE],
                    )
                    if next_token.type is TokenType.KEYWORD_STATE:
                        self.parse_state_declaration(state_node, next_token)
                    elif next_token.type is TokenType.CLOSE_CURLY_BRACKET:
                        break
                    else:
                        self.parse_state_transition(state_node, next_token)

        LOGGER.debug("end of state_declaration")

    def parse_state_transition(self, parent_node, first_token):
        LOGGER.debug("start of state_transition")
        # Create node for production rule
        transition_token = Token(
            type=TokenType.state_transition, start_line=first_token.start_line
        )
        transition_node = parent_node.make_child(transition_token)

        # Add the first token
        transition_node.make_child(first_token)

        # Look for <--, or --> token
        next_token = self.find_tokens(
            tokens_to_find=[TokenType.ARROW],
            tokens_to_skip=[TokenType.WHITESPACE],
        )
        transition_node.make_child(next_token)

        # Look for [*] or name token
        next_token = self.find_tokens(
            tokens_to_find=[TokenType.INITIAL_FINAL_STATE, TokenType.NAME],
            tokens_to_skip=[TokenType.WHITESPACE],
        )
        transition_node.make_child(next_token)

        # Look for newline or : token
        next_token = self.find_tokens(
            tokens_to_find=[TokenType.NEWLINE, TokenType.COLON],
            tokens_to_skip=[TokenType.WHITESPACE],
        )

        if next_token.type is TokenType.NEWLINE:
            # End of state transition
            return

        # Look for a label
        next_token = self.find_tokens(
            tokens_to_find=[TokenType.LABEL],
            tokens_to_skip=[TokenType.WHITESPACE],
        )
        transition_node.make_child(next_token)

        LOGGER.debug("end of state_transition")

    def parse_note_declaration(self, parent_node, first_token):
        LOGGER.debug("start of note_declaration")
        # Create node for production rule
        note_token = Token(
            type=TokenType.note_declaration, start_line=first_token.start_line
        )
        note_node = parent_node.make_child(note_token)

        # Add the first token
        note_node.make_child(first_token)

        # Look for "left of", "right of" or quotation
        next_token = self.find_tokens(
            tokens_to_find=[
                TokenType.KEYWORD_LEFT_OF,
                TokenType.KEYWORD_RIGHT_OF,
                TokenType.QUOTATION,
            ],
            tokens_to_skip=[TokenType.WHITESPACE],
        )

        if next_token.type is TokenType.QUOTATION:
            # Look for label
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.LABEL],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            note_node.make_child(next_token)

            # Look for end quotation
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.QUOTATION],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

            # Look for "as"
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.KEYWORD_AS],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            note_node.make_child(next_token)

            # Look for note name
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.NAME],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            note_node.make_child(next_token)
        else:
            note_node.make_child(next_token)

            # Look for state name
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.NAME],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            note_node.make_child(next_token)

            # Look for colon or newline
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.COLON, TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

            if next_token.type is TokenType.COLON:
                note_node.make_child(next_token)

                # Look for label
                next_token = self.find_tokens(
                    tokens_to_find=[TokenType.LABEL],
                    tokens_to_skip=[TokenType.WHITESPACE],
                )
                note_node.make_child(next_token)
            else:
                while True:
                    # Look for labels or end note
                    next_token = self.find_tokens(
                        tokens_to_find=[TokenType.KEYWORD_END, TokenType.LABEL],
                        tokens_to_skip=[TokenType.WHITESPACE, TokenType.NEWLINE],
                    )

                    if next_token.type is TokenType.KEYWORD_END:
                        self.find_tokens(
                            tokens_to_find=[TokenType.KEYWORD_NOTE],
                            tokens_to_skip=[TokenType.WHITESPACE],
                        )
                        break
                    else:
                        note_node.make_child(next_token)

        LOGGER.debug("end of note_declaration")
