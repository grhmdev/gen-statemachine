import unittest
from tests.utilities import TestCaseBase

from gen_statemachine.model import Builder, StateMachine
from gen_statemachine.frontend import Token, TokenType, ParseTree, Node


class TestBuilder(TestCaseBase):
    def test_empty_tree(self):
        parse_tree = ParseTree()

        builder = Builder()
        model = builder.build_model_from(parse_tree)

        self.assertEqual(len(model.region.states), 0)

    def test_state_declaration_token(self):
        """Tests model generation from a parse tree with a single state declaration token"""
        parse_tree = ParseTree()
        state_declaration_node = parse_tree.root_node.make_child(
            Token(TokenType.state_declaration)
        )
        state_declaration_node.make_child(Token(TokenType.KEYWORD_STATE))
        state_declaration_node.make_child(Token(TokenType.NAME, 0, 0, "STATE"))

        builder = Builder()
        model = builder.build_model_from(parse_tree)

        self.assertEqual(len(model.region.states), 1)
        state = list(model.region.states.values())[0]
        self.assertEqual(state.name, "STATE")


if __name__ == "__main__":
    unittest.main()
