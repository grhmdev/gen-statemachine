from re import S
from typing import TextIO, List, Callable, NewType, Optional
from dataclasses import dataclass, field

from .lexer import LOGGER, Lexer
from .tokens import Token, TokenType


@dataclass
class Node:
    token: Optional[Token] = None
    children: List["Node"] = field(default_factory=list)
    parent: Optional["Node"] = None

    def make_child(self, token: Token) -> "Node":
        assert type(token) is Token
        n = Node(token=token)
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


@dataclass
class ParseTree:
    root_node: Node = field(default_factory=Node)

    def __str__(self):
        return self.root_node.to_str()


@dataclass
class ParseError(RuntimeError):
    error_message: str
    file_name: Optional[str] = None
    line_no: int = 0
    column_no: int = 0

    def __str__(self):
        return f"""
        =======================================
        ʘ︵ʘ oh no!!!
        Parse error @ [{self.file_name}:{self.line_no}:{self.column_no}]
          {self.message}
        =======================================
        """

    def __repr__(self) -> str:
        return self.__str__()


class Parser:
    """
    This parser is responsible for creating "setences" out of the "words" found by the
    lexer. It drives the parser by telling it exactly what to look for, and what to discard.
    If a word token is found that doesn't match the current sentence being parsed, then a
    `ParseError` is raised.
    """

    def __init__(self):
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
                    TokenType.START_BLOCK_COMMENT,
                    TokenType.APOSTROPHE,
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
            elif token.type in [TokenType.START_BLOCK_COMMENT, TokenType.APOSTROPHE]:
                self.parse_comment(self.parse_tree.root_node, token)
            elif token.type is TokenType.KEYWORD_NOTE:
                self.parse_note_declaration(self.parse_tree.root_node, token)
            elif token.type in [TokenType.INITIAL_FINAL_STATE, TokenType.NAME]:
                self.parse_transition_declaration_or_state_label(
                    self.parse_tree.root_node, token
                )

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

    def parse_transition_declaration_or_state_label(
        self, parent_node: Node, first_token: Token
    ):
        # Look for arrow or colon to determine production rule
        second_token = self.find_tokens(
            tokens_to_find=[TokenType.ARROW, TokenType.COLON],
            tokens_to_skip=[TokenType.WHITESPACE],
        )
        if second_token.type is TokenType.ARROW:
            self.parse_transition_declaration(parent_node, first_token, second_token)
        else:
            self.parse_state_label(parent_node, first_token, second_token)

    def parse_state_declaration(self, parent_node: Node, first_token: Token):
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

        if next_token.type is TokenType.NAME:
            state_node.make_child(next_token)
        else:
            state_token.type = TokenType.state_alias_declaration

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

        # Look for stereotype, {, :, or newline
        next_token = self.find_tokens(
            tokens_to_find=[
                TokenType.STEREOTYPE_CHOICE,
                TokenType.STEREOTYPE_END,
                TokenType.STEREOTYPE_ENTRY_POINT,
                TokenType.STEREOTYPE_EXIT_POINT,
                TokenType.STEREOTYPE_INPUT_PIN,
                TokenType.STEREOTYPE_OUTPUT_PIN,
                TokenType.STEREOTYPE_EXPANSION_INPUT,
                TokenType.STEREOTYPE_EXPANSION_OUTPUT,
                TokenType.STEREOTYPE_ANY,
                TokenType.OPEN_CURLY_BRACKET,
                TokenType.COLON,
                TokenType.NEWLINE,
            ],
            tokens_to_skip=[TokenType.WHITESPACE],
        )

        if next_token.type in [
            TokenType.STEREOTYPE_CHOICE,
            TokenType.STEREOTYPE_END,
            TokenType.STEREOTYPE_ENTRY_POINT,
            TokenType.STEREOTYPE_EXIT_POINT,
            TokenType.STEREOTYPE_INPUT_PIN,
            TokenType.STEREOTYPE_OUTPUT_PIN,
            TokenType.STEREOTYPE_EXPANSION_INPUT,
            TokenType.STEREOTYPE_EXPANSION_OUTPUT,
            TokenType.STEREOTYPE_ANY,
        ]:
            state_node.make_child(next_token)
            # Look for {, :, or newline
            next_token = self.find_tokens(
                tokens_to_find=[
                    TokenType.OPEN_CURLY_BRACKET,
                    TokenType.COLON,
                    TokenType.NEWLINE,
                ],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

        if next_token.type is TokenType.OPEN_CURLY_BRACKET:
            # Look for nested state declarations and state transitions
            while True:
                next_token = self.find_tokens(
                    tokens_to_find=[
                        TokenType.KEYWORD_STATE,
                        TokenType.INITIAL_FINAL_STATE,
                        TokenType.APOSTROPHE,
                        TokenType.START_BLOCK_COMMENT,
                        TokenType.NAME,
                        TokenType.CLOSE_CURLY_BRACKET,
                    ],
                    tokens_to_skip=[TokenType.WHITESPACE, TokenType.NEWLINE],
                )
                if next_token.type is TokenType.KEYWORD_STATE:
                    self.parse_state_declaration(state_node, next_token)
                elif next_token.type is TokenType.CLOSE_CURLY_BRACKET:
                    break
                elif next_token.type in [
                    TokenType.START_BLOCK_COMMENT,
                    TokenType.APOSTROPHE,
                ]:
                    self.parse_comment(state_node, next_token)
                else:
                    self.parse_transition_declaration_or_state_label(
                        state_node, next_token
                    )
        elif next_token.type is TokenType.COLON:
            # Look for label
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.LABEL],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            state_node.make_child(next_token)

        LOGGER.debug("end of state_declaration")

    def parse_transition_declaration(
        self, parent_node: Node, name_token: Token, arrow_token: Token
    ):
        LOGGER.debug("start of transition_declaration")
        # Create node for production rule
        transition_token = Token(
            type=TokenType.transition_declaration, start_line=name_token.start_line
        )
        transition_node = parent_node.make_child(transition_token)

        # Add the first tokens
        transition_node.make_child(name_token)
        transition_node.make_child(arrow_token)

        # Look for [*] or name token
        next_token = self.find_tokens(
            tokens_to_find=[TokenType.INITIAL_FINAL_STATE, TokenType.NAME],
            tokens_to_skip=[TokenType.WHITESPACE],
        )
        transition_node.make_child(next_token)

        # Look for :, stereotype or newline
        next_token = self.find_tokens(
            tokens_to_find=[
                TokenType.COLON,
                TokenType.STEREOTYPE_ANY,
                TokenType.NEWLINE,
            ],
            tokens_to_skip=[TokenType.WHITESPACE],
        )

        if next_token.type is TokenType.STEREOTYPE_ANY:
            transition_node.make_child(next_token)
            # Look for : or newline
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.COLON, TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

        if next_token.type is TokenType.NEWLINE:
            # End of state transition
            return

        transition_node.make_child(next_token)

        # Look for [condition] or label
        next_token = self.find_tokens(
            tokens_to_find=[TokenType.CONDITION, TokenType.LABEL],
            tokens_to_skip=[TokenType.WHITESPACE],
        )

        if next_token.type is TokenType.CONDITION:
            transition_node.make_child(next_token)
            # Look for label or newline
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.LABEL, TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

        if next_token.type is TokenType.LABEL:
            transition_node.make_child(next_token)

        LOGGER.debug("end of transition_declaration")

    def parse_note_declaration(self, parent_node: Node, first_token: Token):
        LOGGER.debug("start of note_declaration")
        # Create node for production rule
        note_token = Token(
            type=TokenType.anchored_note_declaration, start_line=first_token.start_line
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
            note_token.type = TokenType.floating_note_declaration

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
                    note_node.make_child(next_token)

                    if next_token.type is TokenType.KEYWORD_END:
                        next_token = self.find_tokens(
                            tokens_to_find=[TokenType.KEYWORD_NOTE],
                            tokens_to_skip=[TokenType.WHITESPACE],
                        )
                        note_node.make_child(next_token)
                        break

        LOGGER.debug("end of note_declaration")

    def parse_state_label(
        self, parent_node: Node, name_token: Token, colon_token: Token
    ):
        LOGGER.debug("start of state_label")
        # Create node for production rule
        state_label_token = Token(
            type=TokenType.state_label, start_line=name_token.start_line
        )
        state_label_node = parent_node.make_child(state_label_token)

        # Add the first tokens
        state_label_node.make_child(name_token)
        state_label_node.make_child(colon_token)

        # Look for label
        next_token = self.find_tokens(
            tokens_to_find=[TokenType.LABEL],
            tokens_to_skip=[TokenType.WHITESPACE],
        )
        state_label_node.make_child(next_token)

        LOGGER.debug("end of state_label")

    def parse_comment(self, parent_node: Node, first_token: Token):
        LOGGER.debug("start of comment")
        # Create node for production rule
        comment_token = Token(type=TokenType.comment, start_line=first_token.start_line)
        comment_node = parent_node.make_child(comment_token)

        # Add the first token
        comment_node.make_child(first_token)

        if first_token.type is TokenType.APOSTROPHE:
            # This is a single line comment
            next_token = self.find_tokens(
                tokens_to_find=[TokenType.LABEL],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            comment_node.make_child(next_token)
        else:
            # This is a block comment, that could contain newlines
            while True:
                next_token = self.find_tokens(
                    tokens_to_find=[TokenType.END_BLOCK_COMMENT, TokenType.LABEL],
                    tokens_to_skip=[TokenType.WHITESPACE, TokenType.NEWLINE],
                )
                comment_node.make_child(next_token)

                if next_token.type is TokenType.END_BLOCK_COMMENT:
                    break

        LOGGER.debug("end of comment")
