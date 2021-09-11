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


def lookup_vertex(statemachine: StateMachine, decl_node: ParseTreeNode, region: Region):
    """For a vertex declaration (e.g. state, choice), looks for an existing entity for that vertex in the same statemachine region"""
    state_name = extract_first_token(decl_node, TokenType.NAME).text
    return next(
        filter(
            lambda v: v.name == state_name,
            statemachine.vertices().values(),
        ),
        None,
    )


class ChoiceBuilder:
    """Creates `ChoicePseudoState` objects from state_declaration expressions"""

    def __init__(self, statemachine: StateMachine, state_decl_node: ParseTreeNode):
        self.statemachine = statemachine
        self.state_decl_node = state_decl_node

    def build(self) -> Choice:
        self.choice = self.statemachine.new_choice()
        LOGGER.debug(f"Adding {self.choice.id}")
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
            self.choice.stereotype = trim_stereotype_text(stereotype_token.text)

    def add_description(self):
        if label_tokens := find_all_tokens(self.state_decl_node, [TokenType.LABEL]):
            self.choice.description = label_tokens[-1].text


class StateBuilder:
    """
    Creates `State` objects from state_declaration and state_alias_declaration expressions.
    It is possible that a state is 'declared' multiple times, but with each declaration providing
    new information. It is important to not re-create the state and sub regions on subsequent
    declarations.
    """

    def __init__(
        self, statemachine: StateMachine, region: Region, state_decl_node: ParseTreeNode
    ):
        self.statemachine = statemachine
        self.region = region
        self.state_decl_node = state_decl_node

    def build(self) -> State:
        new_state = self.statemachine.new_state()
        LOGGER.debug(f"Adding {new_state.id}")
        return self.update(new_state)

    def update(self, state: State) -> State:
        self.state = state
        self.state.name = extract_first_token(self.state_decl_node, TokenType.NAME).text
        self.add_stereotype()
        self.add_action()
        self.add_regions()

        if len(self.state.sub_regions) > 0:
            self.state.type = StateType.COMPOSITE
        else:
            self.state.type = StateType.SIMPLE

        return self.state

    def add_stereotype(self):
        if stereotype_token := find_first_token(
            self.state_decl_node, [TokenType.STEREOTYPE_ANY]
        ):
            self.state.stereotype = trim_stereotype_text(stereotype_token.text)

    def add_action(self):
        if action_token := find_first_token(self.state_decl_node, [TokenType.BEHAVIOR]):
            action = self.statemachine.new_action()
            action.text = action_token.text
            if action.text.startswith("exit/") or action.text.startswith("exit /"):
                action.text = action.text[action.text.index("/") + 1 :].strip()
                self.state.exit_actions.append(action)
            elif action.text.startswith("entry/") or action.text.startswith("entry /"):
                action.text = action.text[action.text.index("/") + 1 :].strip()
                self.state.entry_actions.append(action)
            else:
                self.state.entry_actions.append(action)

    def add_regions(self):
        if declarations_node := next(
            filter(
                lambda c: c.token.type is TokenType.declarations,
                self.state_decl_node.children,
            ),
            None,
        ):
            builder = RegionBuilder(self.statemachine, declarations_node)
            if self.state.sub_regions:
                builder.update(self.state.sub_regions[0])
            else:
                sub_region = builder.build()
                sub_region.state = self.state
                self.state.sub_regions.append(sub_region)


class TransitionBuilder:
    """Creates `Transition` objects from transition_declaration expressions"""

    def __init__(
        self,
        statemachine: StateMachine,
        region: Region,
        transition_decl_node: ParseTreeNode,
    ):
        self.statemachine = statemachine
        self.region = region
        self.model_vertices = list(self.statemachine.vertices().values())
        self.transition_decl_node = transition_decl_node
        self.transition_label_node = next(
            filter(
                lambda n: n.token.type is TokenType.transition_label,
                self.transition_decl_node.children,
            ),
            None,
        )

    def build(self) -> Transition:
        self.transition = self.statemachine.new_transition()
        LOGGER.debug(f"Adding {self.transition.id}")

        self.add_source_and_target()
        self.add_stereotype()
        if self.transition_label_node:
            self.add_event()
            self.add_guard()
            self.add_action()

        self.transition.type = TransitionType.INTERNAL

        return self.transition

    def add_stereotype(self):
        if stereotype_token := find_first_token(
            self.transition_decl_node, [TokenType.STEREOTYPE_ANY]
        ):
            self.transition.stereotype = trim_stereotype_text(stereotype_token.text)

    def add_source_and_target(self):
        vertex_tokens = find_all_tokens(
            self.transition_decl_node, [TokenType.NAME, TokenType.INITIAL_FINAL_STATE]
        )
        assert len(vertex_tokens) == 2

        source_token = vertex_tokens[0]
        target_token = vertex_tokens[1]

        if source_token.type is TokenType.NAME:
            # Find source vertex by name
            source_name = source_token.text
            source_vertex = next(
                filter(lambda e: e.name == source_name, self.model_vertices)
            )
            self.transition.source = source_vertex
            source_vertex.outgoing_transitions.append(self.transition)
        else:
            # [*] used as a transition source is an initial psuedo-state
            self.transition.source = self.region.initial_state
            self.region.initial_state.outgoing_transitions.append(self.transition)

        if target_token.type is TokenType.NAME:
            # Find target vertex by name
            target_name = target_token.text
            target_vertex = next(
                filter(lambda e: e.name == target_name, self.model_vertices)
            )
            self.transition.target = target_vertex
            target_vertex.incoming_transitions.append(self.transition)
        else:
            # [*] used as a transition target is a terminal psuedo-state
            self.transition.target = self.region.terminal_state
            self.region.terminal_state.incoming_transitions.append(self.transition)

    def add_event(self):
        if event_token := find_first_token(
            self.transition_label_node, [TokenType.TRIGGER]
        ):
            self.transition.trigger = self.statemachine.new_event()
            self.transition.trigger.name = event_token.text

    def add_guard(self):
        if guard_token := find_first_token(
            self.transition_label_node, [TokenType.GUARD]
        ):
            self.transition.guard = self.statemachine.new_guard()
            self.transition.guard.condition = guard_token.text

    def add_action(self):
        if action_token := find_first_token(
            self.transition_label_node, [TokenType.BEHAVIOR]
        ):
            self.transition.action = self.statemachine.new_action()
            self.transition.action.text = action_token.text


class RegionBuilder:
    """Creates `Region` objects from a sequence of PUML expressions"""

    def __init__(self, statemachine: StateMachine, declarations_node: ParseTreeNode):
        self.statemachine = statemachine
        self.declarations_node = declarations_node

    def build(self) -> Region:
        new_region = self.statemachine.new_region()
        LOGGER.debug(f"Adding {new_region.id}")
        new_region.initial_state = self.statemachine.new_initial_state()
        new_region.initial_state.region = new_region
        new_region.terminal_state = self.statemachine.new_terminal_state()
        new_region.terminal_state.region = new_region
        return self.update(new_region)

    def update(self, existing_region: Region) -> Region:
        self.region = existing_region
        for node in self.declarations_node.children:
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
                    self.add_state(node)
                else:
                    raise RuntimeError(f"Unhandled stereotype {stereotype_token.type}")
            elif node.token.type is TokenType.transition_declaration:
                self.add_transition(node)
            else:
                LOGGER.debug(f"Skipping {node.token}")

        return self.region

    def add_state(self, node: ParseTreeNode):
        builder = StateBuilder(self.statemachine, self.region, node)
        if state := lookup_vertex(self.statemachine, node, self.region):
            builder.update(state)
        else:
            state = builder.build()
            state.region = self.region
            self.region.sub_vertices.append(state)

    def add_choice(self, node: ParseTreeNode):
        choice = ChoiceBuilder(self.statemachine, node).build()
        choice.region = self.region
        self.region.sub_vertices.append(choice)

    def add_transition(self, node: ParseTreeNode):
        transition = TransitionBuilder(self.statemachine, self.region, node).build()
        self.region.transitions.append(transition)


class ModelBuilder:
    """Generates a new `StateMachine` object from a ParseTree"""

    def __init__(self):
        self.statemachine: StateMachine = None

    def build(self, parse_tree: ParseTree) -> StateMachine:
        # Create statemachine
        self.statemachine = StateMachine(id="statemachine")
        self.statemachine.name = "statemachine"

        # Each statemachine starts with a top level region container
        declarations_node = next(
            filter(
                lambda c: c.token.type is TokenType.declarations,
                parse_tree.root_node.children,
            )
        )
        self.statemachine.region = RegionBuilder(
            self.statemachine, declarations_node
        ).build()
        return self.statemachine
