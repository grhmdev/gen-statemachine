from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    UNKNOWN = auto()
    EOF = auto()

    # Terminal tokens / "words"
    WHITESPACE = auto()
    # \n
    NEWLINE = auto()
    # state
    KEYWORD_STATE = auto()
    # @startuml
    KEYWORD_START_UML = auto()
    # @enduml
    KEYWORD_END_UML = auto()
    # as
    KEYWORD_AS = auto()
    # note
    KEYWORD_NOTE = auto()
    # left of
    KEYWORD_LEFT_OF = auto()
    # right of
    KEYWORD_RIGHT_OF = auto()
    # end
    KEYWORD_END = auto()
    # [*]
    INITIAL_FINAL_STATE = auto()
    # -->
    ARROW = auto()
    # Idle_1
    NAME = auto()
    # this is a label
    LABEL = auto()
    # evDoSomething
    TRIGGER = auto()
    # a > b
    GUARD = auto()
    # do_something();
    BEHAVIOR = auto()
    # :
    COLON = auto()
    # {
    OPEN_CURLY_BRACKET = auto()
    # }
    CLOSE_CURLY_BRACKET = auto()
    # [
    OPEN_SQ_BRACKET = auto()
    # ]
    CLOSE_SQ_BRACKET = auto()
    # "
    QUOTATION = auto()
    # '
    APOSTROPHE = auto()
    # /
    FORWARD_SLASH = auto()
    # /'
    START_BLOCK_COMMENT = auto()
    # '/
    END_BLOCK_COMMENT = auto()
    # <<stereotype>>
    STEREOTYPE_ANY = auto()
    # <<choice>>
    STEREOTYPE_CHOICE = auto()
    # <<end>>
    STEREOTYPE_END = auto()
    # <<entryPoint>>
    STEREOTYPE_ENTRY_POINT = auto()
    # <<exitPoint>>
    STEREOTYPE_EXIT_POINT = auto()
    # <<inputPin>>
    STEREOTYPE_INPUT_PIN = auto()
    # <<outputPin>>
    STEREOTYPE_OUTPUT_PIN = auto()
    # <<expansionInput>>
    STEREOTYPE_EXPANSION_INPUT = auto()
    # <<expansionOutput>>
    STEREOTYPE_EXPANSION_OUTPUT = auto()

    # Production rules / "sentences"
    root = auto()
    declarations = auto()
    # state Disabled
    state_declaration = auto()
    # state "Powered On" as ON
    state_alias_declaration = auto()
    # Enabled : it is on
    state_label = auto()
    # Enabled --> Disabled
    transition_declaration = auto()
    # evDoSomething [is_enabled()] / do_something();
    transition_label = auto()
    # note right of Disabled
    anchored_note_declaration = auto()
    # note "What is this?" as Note1
    floating_note_declaration = auto()
    # 'This is a comment
    comment = auto()

    def __str__(self):
        return self.name


patterns = {
    TokenType.WHITESPACE: r"^[ \t]+\Z",
    TokenType.NEWLINE: r"^[\n]+\Z",
    TokenType.KEYWORD_STATE: r"^state\Z",
    TokenType.KEYWORD_START_UML: r"^@startuml\Z",
    TokenType.KEYWORD_END_UML: r"^@enduml\Z",
    TokenType.KEYWORD_AS: r"^as\Z",
    TokenType.INITIAL_FINAL_STATE: r"^\[\*\]\Z",
    TokenType.ARROW: r"^-(up|down|left|right)?(\[.*\])?->\Z",
    TokenType.NAME: r"^[a-zA-Z0-9_]+\Z",
    TokenType.LABEL: r"^(?! )[a-zA-Z0-9 ?!,.\(\)\\/]+\Z",
    TokenType.TRIGGER: r"^(?! )((?!\[|\/).)+\Z",
    TokenType.GUARD: r"^(?! )((?!\]|\/).)+\Z",
    TokenType.BEHAVIOR: r"^(?! ).+\Z",
    TokenType.COLON: r"^:\Z",
    TokenType.OPEN_CURLY_BRACKET: r"^{\Z",
    TokenType.CLOSE_CURLY_BRACKET: r"^}\Z",
    TokenType.OPEN_SQ_BRACKET: r"^\[\Z",
    TokenType.CLOSE_SQ_BRACKET: r"^\]\Z",
    TokenType.QUOTATION: r'^"\Z',
    TokenType.APOSTROPHE: r"^'\Z",
    TokenType.FORWARD_SLASH: r"^/\Z",
    TokenType.START_BLOCK_COMMENT: r"^/'\Z",
    TokenType.END_BLOCK_COMMENT: r"^'/\Z",
    TokenType.KEYWORD_NOTE: r"^note\Z",
    TokenType.KEYWORD_LEFT_OF: r"^left of\Z",
    TokenType.KEYWORD_RIGHT_OF: r"^right of\Z",
    TokenType.KEYWORD_END: r"^end\Z",
    TokenType.STEREOTYPE_ANY: r"^<<.+>>\Z",
    TokenType.STEREOTYPE_CHOICE: r"^<<choice>>\Z",
    TokenType.STEREOTYPE_END: r"^<<end>>\Z",
    TokenType.STEREOTYPE_ENTRY_POINT: r"^<<entryPoint>>\Z",
    TokenType.STEREOTYPE_EXIT_POINT: r"^<<exitPoint>>\Z",
    TokenType.STEREOTYPE_INPUT_PIN: r"^<<inputPin>>\Z",
    TokenType.STEREOTYPE_OUTPUT_PIN: r"^<<outputPin>>\Z",
    TokenType.STEREOTYPE_EXPANSION_INPUT: r"^<<expansionInput>>\Z",
    TokenType.STEREOTYPE_EXPANSION_OUTPUT: r"^<<expansionOutput>>\Z",
}


@dataclass
class Token:
    type: TokenType = TokenType.UNKNOWN
    start_line: int = 0
    start_col: int = 0
    text: str = ""

    def __str__(self) -> str:
        return "{},{},{}".format(
            self.type, self.start_line, self.text.replace("\n", "\\n")
        )
