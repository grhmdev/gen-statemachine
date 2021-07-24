import logging
from typing import Optional, List, Type

from gen_statemachine.frontend import ParseTree
from gen_statemachine.frontend.tokens import Token, TokenType, STEREOTYPE_TOKEN_TYPES
from gen_statemachine.frontend import Node as ParseTreeNode
from .model import *

LOGGER = logging.getLogger(__name__)


def find_first_token(
    node: ParseTreeNode, token_types: List[TokenType]
) -> Optional[Token]:
    """Returns the first child token that matches an item in `token_types` or `None` if not found"""
    for child in node.children:
        if child.token and child.token.type in token_types:
            return child.token
    return None


def find_all_tokens(node: ParseTreeNode, token_types: List[TokenType]) -> List[Token]:
    """Returns all child tokens that match an item in `token_types`"""
    found_tokens = []
    for child in node.children:
        if child.token and child.token.type in token_types:
            found_tokens.append(child.token)
    return found_tokens


def extract_first_token(node: ParseTreeNode, token_type: TokenType) -> Token:
    """Returns the first child token that matches the token type or raises error if not found"""
    if found_token := find_first_token(node, [token_type]):
        return found_token
    raise RuntimeError(f"Child token not found matching {token_type}")


def trim_stereotype_text(stereotype_text: str) -> str:
    """Removes angle brackets from stereotypes, e.g. converts '<<stereotype>>' into 'stereotype'"""
    return stereotype_text.strip("<>")


class ChoiceFactory:
    """Creates `ChoicePseudoState` objects from state_declaration expressions"""

    def __init__(self, statemachine: StateMachine, state_decl_node: ParseTreeNode):
        self.statemachine = statemachine
        self.state_decl_node = state_decl_node

    def create_choice(self) -> Choice:
        self.choice = self.statemachine.new_choice()
        LOGGER.debug(f"Adding {self.choice.id} to model")
        self.choice.name = extract_first_token(
            self.state_decl_node, TokenType.NAME
        ).text
        self.add_stereotype()
        self.add_description()
        return self.choice

    def add_stereotype(self):
        if stereotype_token := find_first_token(
            self.state_decl_node, [TokenType.STEREOTYPE_ANY]
        ):
            self.state.stereotype = trim_stereotype_text(stereotype_token.text)

    def add_description(self):
        if label_tokens := find_all_tokens(self.state_decl_node, [TokenType.LABEL]):
            self.state.description = label_tokens[-1].text


class StateFactory:
    """Creates `State` objects from state_declaration and state_alias_declaration expressions"""

    def __init__(self, statemachine: StateMachine, state_decl_node: ParseTreeNode):
        self.statemachine = statemachine
        self.state_decl_node = state_decl_node

    def create_state(self) -> State:
        self.state = self.statemachine.new_state()
        LOGGER.debug(f"Adding {self.state.id} to model")

        self.state.name = extract_first_token(self.state_decl_node, TokenType.NAME).text
        self.add_stereotype()
        self.add_description()
        self.add_regions()

        if self.state.regions:
            self.state.type = StateType.COMPOSITE
        else:
            self.state.type = StateType.SIMPLE

        return self.state

    def add_stereotype(self):
        if stereotype_token := find_first_token(
            self.state_decl_node, [TokenType.STEREOTYPE_ANY]
        ):
            self.state.stereotype = trim_stereotype_text(stereotype_token.text)

    def add_description(self):
        if label_tokens := find_all_tokens(self.state_decl_node, [TokenType.LABEL]):
            self.state.description = label_tokens[-1].text

    def add_regions(self):
        open_bracket_node = next(
            filter(
                lambda n: n.token.type is TokenType.OPEN_CURLY_BRACKET,
                self.state_decl_node.children,
            ),
            None,
        )
        if open_bracket_node:
            index_of_open_bracket = self.state_decl_node.children.index(
                open_bracket_node
            )
            nested_nodes = self.state_decl_node.children[index_of_open_bracket:]
            region_factory = RegionFactory(self.statemachine, nested_nodes)
            sub_region = region_factory.create_region()
            self.state.regions[sub_region.id] = sub_region


class RegionFactory:
    """Creates `Region` objects from a sequence of PUML expressions"""

    def __init__(self, statemachine: StateMachine, region_nodes: List[ParseTreeNode]):
        self.statemachine = statemachine
        self.nodes = region_nodes

    def create_region(self) -> Region:
        self.region = self.statemachine.new_region()
        LOGGER.debug(f"Adding {self.region.id} to model")

        for node in self.nodes:
            if not node.token:
                raise RuntimeError(f"Node found without token")

            if node.token.type in [
                TokenType.state_declaration,
                TokenType.state_alias_declaration,
            ]:
                stereotype_token = find_first_token(node, STEREOTYPE_TOKEN_TYPES)
                if (
                    not stereotype_token
                    or stereotype_token.type is TokenType.STEREOTYPE_ANY
                ):
                    self.add_state(node)
                elif stereotype_token.type is TokenType.STEREOTYPE_CHOICE:
                    self.add_choice(node)
                elif stereotype_token.type in [
                    TokenType.STEREOTYPE_END,
                    TokenType.STEREOTYPE_ENTRY_POINT,
                    TokenType.STEREOTYPE_EXIT_POINT,
                    TokenType.STEREOTYPE_INPUT_PIN,
                    TokenType.STEREOTYPE_OUTPUT_PIN,
                    TokenType.STEREOTYPE_EXPANSION_INPUT,
                    TokenType.STEREOTYPE_EXPANSION_OUTPUT,
                ]:
                    # TODO:
                    pass
                else:
                    raise RuntimeError(f"Unhandled stereotype {stereotype_token.type}")
            else:
                LOGGER.debug(f"Skipping {node.token}")

        return self.region

    def add_state(self, node: ParseTreeNode):
        factory = StateFactory(self.statemachine, node)
        state = factory.create_state()
        self.region.states[state.id] = state

    def add_choice(self, node: ParseTreeNode):
        factory = ChoiceFactory(self.statemachine, node)
        choice = factory.create_choice()
        self.region.choices[choice.id] = choice


class ModelFactory:
    def __init__(self):
        self.statemachine: StateMachine = None

    def new_statemachine(self, parse_tree: ParseTree) -> StateMachine:
        # Create statemachine
        self.statemachine = StateMachine(id="statemachine")
        self.statemachine.name = "statemachine"

        region_factory = RegionFactory(self.statemachine, parse_tree.root_node.children)
        self.statemachine.region = region_factory.create_region()

        return self.statemachine
