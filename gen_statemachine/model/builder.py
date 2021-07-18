import logging
from typing import Optional, List, Type

from gen_statemachine.frontend import ParseTree
from gen_statemachine.frontend.tokens import Token, TokenType, STEREOTYPE_TOKEN_TYPES
from gen_statemachine.frontend import Node as ParseTreeNode
from . import model

LOGGER = logging.getLogger(__name__)

# class TransitionBuilder:
#     def __init__(self, model: model.FSM):
#         self.transition = model.Transition()
#         self.source_state_node: ParseTreeNode = None
#         self.dest_state_node: ParseTreeNode = None

#     def add_state(self, state_node: ParseTreeNode):
#         if not self.transition.start_state:
#             self.transition
#         if not self.source_state_node:
#             self.source_state_node = state_node
#         else:
#             self.dest_state_node = state_node

#     def add_stereotype(self, stereotype_node: ParseTreeNode):
#         self.transition.stereotype = stereotype_node.token.text

#     def result(self) -> model.Transition: return self.transition


class Builder:
    def __init__(self):
        self.model: model.StateMachine = None

    def build_model_from(self, parse_tree: ParseTree) -> model.StateMachine:
        # Create statemachine
        self.model = model.StateMachine(id="statemachine")
        self.model.name = "statemachine"
        self.model.region = self.create_region(parse_tree.root_node, self.model)
        self.add_entity_to_quick_lookup(self.model.region)
        return self.model

    def add_entity_to_quick_lookup(self, entity: model.Entity):
        LOGGER.debug(f"Adding entity to model: {entity}")
        self.model.entities[entity.id] = entity

    def create_region(self, node: ParseTreeNode, container: model.Entity) -> model.Region:
        region = model.Region(id=f"{container.id}.region1")

        for child in node.children:
            if self.is_state_decl_token(child.token):
                self.create_state(child, region)
            # elif self.is_state_label_token(child.token):
            #     self.create_state(child)
            # elif self.is_state_transition_token(child.token):
            #     self.create_transition(node)
            else:
                LOGGER.debug(f"Skipping {child.token}")

        return region

    def create_state(self, node: ParseTreeNode, region: model.Entity):
        stereotype_token = self.find_token(node, STEREOTYPE_TOKEN_TYPES)


        if not stereotype_token or stereotype_token.type is TokenType.STEREOTYPE_ANY:
            # Create normal state
            vertex = model.State(id=f"{region.id}.state{len(region.states)+1}")
            region.states[vertex.id] = vertex
           # TODO: Handle nested tokens

        elif stereotype_token.type is TokenType.STEREOTYPE_CHOICE:
            # Create choice pseudo-state
            vertex = model.ChoicePseudoState(id=f"{region.id}.choice{len(region.choice_pseudo_states)+1}")
            region.choice_pseudo_states[vertex.id] = vertex
        elif stereotype_token.type in [TokenType.STEREOTYPE_END, TokenType.STEREOTYPE_ENTRY_POINT, TokenType.STEREOTYPE_EXIT_POINT, TokenType.STEREOTYPE_INPUT_PIN, TokenType.STEREOTYPE_OUTPUT_PIN, TokenType.STEREOTYPE_EXPANSION_INPUT, TokenType.STEREOTYPE_EXPANSION_OUTPUT]:
            # TODO
            pass
        else:
            raise RuntimeError(f"Unhandled stereotype {stereotype_token.type}")

        vertex.name = self.extract_token(node, TokenType.NAME).text
        label_tokens = self.find_all_tokens(node, [TokenType.LABEL])
        if len(label_tokens) > 0:
            vertex.description = label_tokens[-1].text
        self.add_entity_to_quick_lookup(vertex)

    # def create_transition(self, node: ParseTreeNode) -> model.State:
    #     transition = model.Transition()
    #     start_state_token, dest_state_token = self.extract_N_tokens(node, [TokenType.NAME, TokenType.INITIAL_FINAL_STATE], 2)

    #     if start_state_token.type is TokenType.INITIAL_FINAL_STATE:
    #         transition.start_state = self.get_or_create_initial_state(node)
    #     else: # NAME
    #         transition.start_state = self.model.get_or_create_state(start_state_token.text)
        
    #     if dest_state_token.type is TokenType.INITIAL_FINAL_STATE:
    #         transition.start_state = self.get_or_create_final_state(node)
    #     else: # NAME
    #         transition.start_state = self.model.get_or_create_state(dest_state_token.text)


    #     transition.start_state = states[0]
    #     transition.destination_state = states[1]

    #     if stereotype_token := self.find_token(node, TokenType.STEREOTYPE_ANY):
    #         transition.stereotype = stereotype_token.text

    #     # TODO: Parse label

    #     return transition


    # Parse Tree Utils

    def is_state_decl_token(self, token: Token):
        return token.type in [TokenType.state_declaration, TokenType.state_alias_declaration]

    def is_state_label_token(self, token: Token):
        return token.type is TokenType.state_label

    def is_state_transition_token(self, token: Token):
        return token.type is TokenType.state_transition

    def extract_token(self, node: ParseTreeNode, token_type: TokenType) -> Token:
        """ Returns the first child token that matches the token type or raises error if not found"""
        if found_token := self.find_token(node, [token_type]):
            return found_token
        raise RuntimeError(f"Child token not found matching {token_type}")

    def find_token(self, node: ParseTreeNode, token_types: List[TokenType]) -> Optional[Token]:
        """ Returns the first child token that matches an item in `token_types` or `None` if not found"""
        for child in node.children:
            if child.token and child.token.type in token_types:
                return child.token
        return None

    def find_all_tokens(self, node: ParseTreeNode, token_types: List[TokenType]) -> List[Token]:
        return [child.token for child in node.children if child.token.type in token_types]

    def extract_N_tokens(self, node: ParseTreeNode, token_types: List[TokenType], N: int) -> List[Token]:
        matches = self.find_all_tokens(node, token_types)
        if len(matches) >= N:
            return matches[:N]
        raise RuntimeError(f"{N} child tokens not found matching {token_types}")