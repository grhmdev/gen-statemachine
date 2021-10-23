import logging
from re import S
from typing import TextIO, List, Callable, NewType, Optional
from dataclasses import dataclass, field

from gen_fsm.frontend.lexer import Lexer
from gen_fsm.frontend.tokens import Token, TokenType
from gen_fsm.frontend.parse_tree import ParseTree, Node
from gen_fsm.error import ProgramError

LOGGER = logging.getLogger(__name__)


class ParseError(ProgramError):
    def __init__(self, detail: str, file_name: str, line_no: int, column_no: int):
        super().__init__(
            f"Parse error @ [{file_name}:{line_no}:{column_no}]" + "\n" + detail
        )


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

    def _find_tokens(
        self, tokens_to_find: List[TokenType], tokens_to_skip: List[TokenType]
    ) -> Token:
        """
        Queries the lexer for the next token that matches one of `tokens_to_find`.
        If the returned token is not in this list, a parse error is raised. If the next
        token is in `tokens_to_skip`, the lexer will ignore it and keeping looking.
        """
        next_token = self.lexer.look_for_tokens(tokens_to_find, tokens_to_skip)

        if next_token.type not in tokens_to_find:
            error_msg = """Unexpected symbols '{}'\nExpected one of {}""".format(
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

    def parse_puml(self, file: TextIO) -> ParseTree:
        self.lexer = Lexer(file)
        self.file_name = file.name
        self.parse_root()
        return self.parse_tree

    def parse_root(self):
        # root = KEYWORD_START_UML [LABEL] NEWLINE declarations KEYWORD_END_UML ;
        root_node = self.parse_tree.root_node

        # KEYWORD_START_UML
        start_token = self._find_tokens(
            tokens_to_find=[TokenType.KEYWORD_START_UML],
            tokens_to_skip=[TokenType.WHITESPACE, TokenType.NEWLINE],
        )
        root_node.add_child(start_token)

        # [LABEL] NEWLINE
        next_token = self._find_tokens(
            tokens_to_find=[TokenType.LABEL, TokenType.NEWLINE],
            tokens_to_skip=[TokenType.WHITESPACE],
        )
        if next_token.type is TokenType.LABEL:
            root_node.add_child(next_token)
            self._find_tokens(
                tokens_to_find=[TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

        # declarations
        end_token = self.parse_declarations(
            root_node, terminal_token=TokenType.KEYWORD_END_UML
        )

        # KEYWORD_END_UML
        root_node.add_child(end_token)

    def parse_declarations(self, parent_node, terminal_token: TokenType) -> Token:
        """Parses declarations until `terminal_token` is found and returned"""
        # declarations = {declaration NEWLINE}+
        declarations_node = parent_node.add_child(Token(TokenType.declarations))

        # declaration = state_declaration
        #             | state_alias_declaration
        #             | transition_declaration
        #             | anchored_note_declaration
        #             | floating_note_declaration
        #             | comment

        # The order of tokens to search for is important here,
        # e.g. KEYWORD_STATE should precede NAME because "state"
        # is also a valid name
        tokens_to_find = [
            terminal_token,
            TokenType.KEYWORD_STATE,
            TokenType.KEYWORD_NOTE,
            TokenType.START_BLOCK_COMMENT,
            TokenType.APOSTROPHE,
            TokenType.INITIAL_FINAL_STATE,
            TokenType.NAME,
        ]
        tokens_to_skip = [TokenType.WHITESPACE, TokenType.NEWLINE]

        # Keep parsing until the terminal token is found, or EOF error
        while True:
            token = self._find_tokens(tokens_to_find, tokens_to_skip)

            if token.type is TokenType.UNKNOWN:
                raise RuntimeError(f"Unknown token found: {token}")
            elif token.type is TokenType.EOF:
                raise RuntimeError(f"End-of-file found before token {terminal_token}")
            elif token.type is terminal_token:
                return token
            elif token.type is TokenType.KEYWORD_STATE:
                self.parse_state_declaration(declarations_node, token)
            elif token.type in [TokenType.START_BLOCK_COMMENT, TokenType.APOSTROPHE]:
                self.parse_comment(declarations_node, token)
            elif token.type is TokenType.KEYWORD_NOTE:
                self.parse_note_declaration(declarations_node, token)
            elif token.type in [TokenType.INITIAL_FINAL_STATE, TokenType.NAME]:
                self.parse_transition_declaration_or_state_label(
                    declarations_node, token
                )

    def parse_transition_declaration_or_state_label(
        self, parent_node: Node, first_token: Token
    ):
        # Look for arrow or colon to determine production rule
        second_token = self._find_tokens(
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
        state_node = parent_node.add_child(state_token)

        state_node.add_child(first_token)

        # Look for state name, or quotation enclosed label
        next_token = self._find_tokens(
            tokens_to_find=[TokenType.NAME, TokenType.QUOTATION],
            tokens_to_skip=[TokenType.WHITESPACE],
        )

        if next_token.type is TokenType.NAME:
            state_node.add_child(next_token)
        else:
            state_token.type = TokenType.state_alias_declaration

            next_token = self._find_tokens(
                tokens_to_find=[TokenType.LABEL], tokens_to_skip=[TokenType.WHITESPACE]
            )
            state_node.add_child(next_token)

            next_token = self._find_tokens(
                tokens_to_find=[TokenType.QUOTATION],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

            next_token = self._find_tokens(
                tokens_to_find=[TokenType.KEYWORD_AS],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            state_node.add_child(next_token)

            next_token = self._find_tokens(
                tokens_to_find=[TokenType.NAME], tokens_to_skip=[TokenType.WHITESPACE]
            )
            state_node.add_child(next_token)

        # Look for stereotype, {, :, or newline
        next_token = self._find_tokens(
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
            state_node.add_child(next_token)
            # Look for {, :, or newline
            next_token = self._find_tokens(
                tokens_to_find=[
                    TokenType.OPEN_CURLY_BRACKET,
                    TokenType.COLON,
                    TokenType.NEWLINE,
                ],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

        if next_token.type is TokenType.OPEN_CURLY_BRACKET:
            # Look for nested state declarations and state transitions
            self.parse_declarations(
                state_node, terminal_token=TokenType.CLOSE_CURLY_BRACKET
            )
        elif next_token.type is TokenType.COLON:
            # Look for entry/exit action or label
            next_token = self._find_tokens(
                tokens_to_find=[
                    TokenType.KEYWORD_ENTRY,
                    TokenType.KEYWORD_EXIT,
                    TokenType.LABEL,
                ],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            if next_token.type is TokenType.LABEL:
                state_node.add_child(next_token)
            else:
                action_token = Token(
                    type=TokenType.entry_action
                    if next_token.type is TokenType.KEYWORD_ENTRY
                    else TokenType.exit_action,
                    start_line=next_token.start_line,
                    start_col=next_token.start_col,
                )
                action_node = state_node.add_child(action_token)
                action_node.add_child(next_token)
                next_token = self._find_tokens(
                    tokens_to_find=[TokenType.FORWARD_SLASH],
                    tokens_to_skip=[TokenType.WHITESPACE],
                )
                action_node.add_child(next_token)
                next_token = self._find_tokens(
                    tokens_to_find=[TokenType.BEHAVIOR],
                    tokens_to_skip=[TokenType.WHITESPACE],
                )
                action_node.add_child(next_token)

        LOGGER.debug("end of state_declaration")

    def parse_transition_declaration(
        self, parent_node: Node, name_token: Token, arrow_token: Token
    ):
        LOGGER.debug("start of transition_declaration")
        # Create node for production rule
        transition_token = Token(
            type=TokenType.transition_declaration, start_line=name_token.start_line
        )
        transition_node = parent_node.add_child(transition_token)

        # Add the first tokens
        transition_node.add_child(name_token)
        transition_node.add_child(arrow_token)

        # Look for [*] or name token
        next_token = self._find_tokens(
            tokens_to_find=[TokenType.INITIAL_FINAL_STATE, TokenType.NAME],
            tokens_to_skip=[TokenType.WHITESPACE],
        )
        transition_node.add_child(next_token)

        # Look for :, stereotype or newline
        next_token = self._find_tokens(
            tokens_to_find=[
                TokenType.COLON,
                TokenType.STEREOTYPE_ANY,
                TokenType.NEWLINE,
            ],
            tokens_to_skip=[TokenType.WHITESPACE],
        )

        if next_token.type is TokenType.STEREOTYPE_ANY:
            transition_node.add_child(next_token)
            # Look for : or newline
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.COLON, TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

        if next_token.type is TokenType.NEWLINE:
            # End of state transition
            return

        transition_node.add_child(next_token)

        label_node = transition_node.add_child(Token(TokenType.transition_label))

        # Look for trigger, [condition] or /
        next_token = self._find_tokens(
            tokens_to_find=[
                TokenType.TRIGGER,
                TokenType.OPEN_SQ_BRACKET,
                TokenType.FORWARD_SLASH,
                TokenType.NEWLINE,
            ],
            tokens_to_skip=[TokenType.WHITESPACE],
        )

        if next_token.type is TokenType.TRIGGER:
            label_node.add_child(next_token)
            next_token = self._find_tokens(
                tokens_to_find=[
                    TokenType.OPEN_SQ_BRACKET,
                    TokenType.FORWARD_SLASH,
                    TokenType.NEWLINE,
                ],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

        if next_token.type is TokenType.OPEN_SQ_BRACKET:
            label_node.add_child(next_token)
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.GUARD],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            label_node.add_child(next_token)

            next_token = self._find_tokens(
                tokens_to_find=[TokenType.CLOSE_SQ_BRACKET],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            label_node.add_child(next_token)

            next_token = self._find_tokens(
                tokens_to_find=[TokenType.FORWARD_SLASH, TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

        if next_token.type is TokenType.FORWARD_SLASH:
            label_node.add_child(next_token)
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.BEHAVIOR, TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            if next_token.type is TokenType.BEHAVIOR:
                label_node.add_child(next_token)

        LOGGER.debug("end of transition_declaration")

    def parse_note_declaration(self, parent_node: Node, first_token: Token):
        LOGGER.debug("start of note_declaration")
        # Create node for production rule
        note_token = Token(
            type=TokenType.anchored_note_declaration, start_line=first_token.start_line
        )
        note_node = parent_node.add_child(note_token)

        # Add the first token
        note_node.add_child(first_token)

        # Look for "left of", "right of" or quotation
        next_token = self._find_tokens(
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
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.LABEL],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            note_node.add_child(next_token)

            # Look for end quotation
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.QUOTATION],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

            # Look for "as"
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.KEYWORD_AS],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            note_node.add_child(next_token)

            # Look for note name
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.NAME],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            note_node.add_child(next_token)
        else:
            note_node.add_child(next_token)

            # Look for state name
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.NAME],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            note_node.add_child(next_token)

            # Look for colon or newline
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.COLON, TokenType.NEWLINE],
                tokens_to_skip=[TokenType.WHITESPACE],
            )

            if next_token.type is TokenType.COLON:
                # Look for label
                next_token = self._find_tokens(
                    tokens_to_find=[TokenType.LABEL],
                    tokens_to_skip=[TokenType.WHITESPACE],
                )
                note_node.add_child(next_token)
            else:
                while True:
                    # Look for labels or end note
                    next_token = self._find_tokens(
                        tokens_to_find=[TokenType.KEYWORD_END, TokenType.LABEL],
                        tokens_to_skip=[TokenType.WHITESPACE, TokenType.NEWLINE],
                    )
                    note_node.add_child(next_token)

                    if next_token.type is TokenType.KEYWORD_END:
                        next_token = self._find_tokens(
                            tokens_to_find=[TokenType.KEYWORD_NOTE],
                            tokens_to_skip=[TokenType.WHITESPACE],
                        )
                        note_node.add_child(next_token)
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
        state_label_node = parent_node.add_child(state_label_token)

        # Add the first tokens
        state_label_node.add_child(name_token)
        state_label_node.add_child(colon_token)

        # Look for entry/exit action or label
        next_token = self._find_tokens(
            tokens_to_find=[
                TokenType.KEYWORD_ENTRY,
                TokenType.KEYWORD_EXIT,
                TokenType.LABEL,
            ],
            tokens_to_skip=[TokenType.WHITESPACE],
        )
        if next_token.type is TokenType.LABEL:
            state_label_node.add_child(next_token)
        else:
            action_token = Token(
                type=TokenType.entry_action
                if next_token.type is TokenType.KEYWORD_ENTRY
                else TokenType.exit_action,
                start_line=next_token.start_line,
                start_col=next_token.start_col,
            )
            action_node = state_label_node.add_child(action_token)
            action_node.add_child(next_token)
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.FORWARD_SLASH],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            action_node.add_child(next_token)
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.BEHAVIOR],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            action_node.add_child(next_token)

        LOGGER.debug("end of state_label")

    def parse_comment(self, parent_node: Node, first_token: Token):
        LOGGER.debug("start of comment")
        # Create node for production rule
        comment_token = Token(type=TokenType.comment, start_line=first_token.start_line)
        comment_node = parent_node.add_child(comment_token)

        # Add the first token
        comment_node.add_child(first_token)

        if first_token.type is TokenType.APOSTROPHE:
            # This is a single line comment
            next_token = self._find_tokens(
                tokens_to_find=[TokenType.LABEL],
                tokens_to_skip=[TokenType.WHITESPACE],
            )
            comment_node.add_child(next_token)
        else:
            # This is a block comment, that could contain newlines
            while True:
                next_token = self._find_tokens(
                    tokens_to_find=[TokenType.END_BLOCK_COMMENT, TokenType.LABEL],
                    tokens_to_skip=[TokenType.WHITESPACE, TokenType.NEWLINE],
                )
                comment_node.add_child(next_token)

                if next_token.type is TokenType.END_BLOCK_COMMENT:
                    break

        LOGGER.debug("end of comment")
