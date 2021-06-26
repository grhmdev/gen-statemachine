from enum import Enum, auto


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
    # :
    COLON = auto()
    # {
    OPEN_CURLY_BRACKET = auto()
    # }
    CLOSE_CURLY_BRACKET = auto()
    # "
    QUOTATION = auto()
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
    # state Disabled
    state_declaration = auto()
    # state "Powered On" as ON
    state_alias_declaration = auto()
    # Enabled : it is on
    state_label = auto()
    # Enabled --> Disabled
    state_transition = auto()
    # note right of Disabled
    anchored_note_declaration = auto()
    # note "What is this?" as Note1
    floating_note_declaration = auto()

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
    TokenType.COLON: r"^:\Z",
    TokenType.OPEN_CURLY_BRACKET: r"^{\Z",
    TokenType.CLOSE_CURLY_BRACKET: r"^}\Z",
    TokenType.QUOTATION: r'^"\Z',
    TokenType.KEYWORD_NOTE: r"^note\Z",
    TokenType.KEYWORD_LEFT_OF: r"^left of\Z",
    TokenType.KEYWORD_RIGHT_OF: r"^right of\Z",
    TokenType.KEYWORD_END: r"^end\Z",
}


class Token:
    def __init__(
        self,
        type: TokenType = TokenType.UNKNOWN,
        start_line: int = 0,
        start_col: int = 0,
        text: str = "",
    ):
        self.type = type
        self.start_line = start_line
        self.start_col = start_col
        self.text = text

    def __str__(self) -> str:
        return "{},{},{}".format(
            self.type, self.start_line, self.text.replace("\n", "\\n")
        )
