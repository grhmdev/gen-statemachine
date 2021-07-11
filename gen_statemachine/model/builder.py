import logging
from typing import Optional, List

from gen_statemachine.frontend import ParseTree
from gen_statemachine.frontend.tokens import Token, TokenType
from gen_statemachine.frontend import Node as ParseTreeNode
from .model import FSM, State, Transition, Event, Action

LOGGER = logging.getLogger(__name__)


class Builder:
    def __init__(self):
        self.model: FSM = None

    def build_model_from(self, parse_tree: ParseTree) -> FSM:
        self.model = FSM()
        self.parse_node(parse_tree.root_node)
        return self.model

    def parse_node(self, node: ParseTreeNode):
        if node.token:
            if node.token.type in [
                TokenType.state_declaration,
                TokenType.state_alias_declaration,
            ]:
                self.create_state(node)

        for child_node in node.children:
            self.parse_node(child_node)

    def create_state(self, node: ParseTreeNode) -> State:
        name_token = self.extract_first_token(node, TokenType.NAME)
        state = self.get_or_create_state(name_token.text)

        # If this state is a sub-state, link it with the parent state
        if self.has_parent_with_token(
            node, TokenType.state_declaration
        ) or self.has_parent_with_token(node, TokenType.state_alias_declaration):
            # TODO
            pass

        return state

    def extract_first_token(self, node: ParseTreeNode, token_type: TokenType) -> Token:
        for child in node.children:
            if child.token and child.token.type == token_type:
                return child.token
        raise RuntimeError(f"Node not found with {token_type}")

    def has_parent_with_token(self, node: ParseTreeNode, token_type: TokenType):
        if node.parent and node.parent.token:
            if node.parent.token.type is token_type:
                return True
        return False

    def get_or_create_state(self, name: str):
        state = self.model.find_state(name)
        if not state:
            LOGGER.debug(f"Creating state: {name}")
            state = self.model.add_state(name)
        return state
