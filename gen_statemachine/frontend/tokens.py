from enum import Enum, auto


class TokenType(Enum):
    UNKNOWN = auto()
    EOF = auto()

    # Terminal tokens, "words"
    # ' '
    WHITESPACE = auto()
    # '\n'
    NEWLINE = auto()
    # 'state'
    KEYWORD_STATE = auto()
    # '@startuml
    KEYWORD_START = auto()
    # '@enduml'
    KEYWORD_END = auto()
    # 'as'
    KEYWORD_AS = auto()
    # '[*]'
    INITIAL_FINAL_STATE = auto()
    # '-->'
    ARROW = auto()
    # 'Idle_1'
    NAME = auto()
    # 'this is a label'
    LABEL = auto()
    # ':'
    COLON = auto()
    # '{'
    OPEN_CURLY_BRACKET = auto()
    # '}'
    CLOSE_CURLY_BRACKET = auto()
    # '"'
    QUOTATION = auto()

    # Production rules, "sentences"
    # state NAME
    state_declaration = auto()
    # state "LABEL" as NAME
    state_alias_declaration = auto()
    # [*] --> NAME
    state_transition = auto()

    def __str__(self):
        return self.name


patterns = {
    TokenType.WHITESPACE: r"^[ \t]+\Z",
    TokenType.NEWLINE: r"^[\n]+\Z",
    TokenType.KEYWORD_STATE: r"^state\Z",
    TokenType.KEYWORD_START: r"^@startuml\Z",
    TokenType.KEYWORD_END: r"^@enduml\Z",
    TokenType.KEYWORD_AS: r"^as\Z",
    TokenType.INITIAL_FINAL_STATE: r"^\[\*\]\Z",
    TokenType.ARROW: r"^-(up|down|left|right)?(\[.*\])?->\Z",
    TokenType.NAME: r"^[a-zA-Z0-9_]+\Z",
    TokenType.LABEL: r"^[a-zA-Z0-9 ]+\Z",
    TokenType.COLON: r"^:\Z",
    TokenType.OPEN_CURLY_BRACKET: r"^{\Z",
    TokenType.CLOSE_CURLY_BRACKET: r"^}\Z",
    TokenType.QUOTATION: r'^"\Z',
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
            self.type, self.text.replace("\n", "\\n"), self.start_line
        )
