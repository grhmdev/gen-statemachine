import unittest
from tests.utilities import TestCaseBase

from gen_statemachine.model.model import StateType
from gen_statemachine.model import ModelFactory
from gen_statemachine.frontend import Token, TokenType, ParseTree


class TestModelFactory(TestCaseBase):
    def test_simple_state_declaration(self):
        """Test a parse tree with a simple state declaration"""
        # Construct tree
        parse_tree = ParseTree()
        declarations_node = parse_tree.root_node.make_child(
            Token(TokenType.declarations)
        )
        state_declaration_node = declarations_node.make_child(
            Token(TokenType.state_declaration)
        )
        state_declaration_node.make_child(Token(TokenType.KEYWORD_STATE))
        state_declaration_node.make_child(Token(TokenType.NAME, 0, 0, "STATE"))
        state_declaration_node.make_child(
            Token(TokenType.STEREOTYPE_ANY, 0, 0, "<<stereotype text>>")
        )
        state_declaration_node.make_child(Token(TokenType.COLON))
        state_declaration_node.make_child(
            Token(TokenType.LABEL, 0, 0, "descriptive text")
        )

        # Generate statemachine
        factory = ModelFactory()
        statemachine = factory.new_statemachine(parse_tree)

        # Assert
        state1 = statemachine.entities["statemachine.state1"]
        self.assertEqual(state1.name, "STATE")
        self.assertEqual(state1.stereotype, "stereotype text")
        self.assertEqual(state1.description, "descriptive text")
        self.assertEqual(state1.type, StateType.SIMPLE)
        self.assertTrue(state1 is statemachine.region.states[state1.id])

    def test_composite_state_declaration(self):
        """Test a parse tree with a composite state declaration"""
        # Construct tree
        parse_tree = ParseTree()
        declarations_node = parse_tree.root_node.make_child(
            Token(TokenType.declarations)
        )
        state_declaration_node = declarations_node.make_child(
            Token(TokenType.state_declaration)
        )
        state_declaration_node.make_child(Token(TokenType.KEYWORD_STATE))
        state_declaration_node.make_child(Token(TokenType.NAME, 0, 0, "STATE1"))
        state_declaration_node.make_child(Token(TokenType.OPEN_CURLY_BRACKET))
        nested_declarations_node = state_declaration_node.make_child(
            Token(TokenType.declarations)
        )
        nested_state_declaration_node = nested_declarations_node.make_child(
            Token(TokenType.state_declaration)
        )
        state_declaration_node.make_child(Token(TokenType.CLOSE_CURLY_BRACKET))

        nested_state_declaration_node.make_child(Token(TokenType.KEYWORD_STATE))
        nested_state_declaration_node.make_child(Token(TokenType.NAME, 0, 0, "STATE2"))

        # Generate statemachine
        factory = ModelFactory()
        statemachine = factory.new_statemachine(parse_tree)

        # Assert
        state1 = statemachine.entities["statemachine.state1"]
        self.assertEqual(state1.name, "STATE1")
        self.assertEqual(state1.type, StateType.COMPOSITE)
        self.assertTrue(state1 is statemachine.region.states[state1.id])

        region2 = statemachine.entities["statemachine.region2"]
        self.assertTrue(region2 is list(state1.regions.values())[0])

        state2 = statemachine.entities["statemachine.state2"]
        self.assertEqual(state2.name, "STATE2")
        self.assertEqual(state2.type, StateType.SIMPLE)
        self.assertTrue(state2 is list(region2.states.values())[0])


if __name__ == "__main__":
    unittest.main()