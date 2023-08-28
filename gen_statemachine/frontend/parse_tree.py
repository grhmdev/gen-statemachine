from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass, field

from gen_statemachine.frontend.tokens import Token, TokenType


class ParseTree:
    """
    Tree structure to hold the tokens parsed from a PlantUML file.
    """

    def __init__(self):
        self.root_node = Node(Token(TokenType.root))

    def __str__(self):
        """
        Recursively prints the nodes in the tree
        """
        return self.root_node.to_str()


@dataclass
class Node:
    token: Token
    children: List["Node"] = field(default_factory=list)
    parent: Optional["Node"] = None

    def add_child(self, token: Token) -> Node:
        """
        Creates a new node and appends it to this node's children
        """
        n = Node(token=token)
        self.children.append(n)
        n.parent = self
        return n

    def to_str(self, depth=0) -> str:
        """
        Recursively prints this node and its children
        """
        s = ("  " * depth) + "└ "
        if self.token:
            s += f"<{self.token.type}>: " + self.token.text.replace("\n", "\\n")
        else:
            s += "root"

        for child in self.children:
            s += "\n" + child.to_str(depth + 1)
        return s
