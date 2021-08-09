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
        self.assertTrue(state1 is statemachine.region.states[0])

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
        self.assertTrue(state1 is statemachine.region.states[0])

        region2 = statemachine.entities["statemachine.region2"]
        self.assertTrue(region2 is state1.regions[0])

        state2 = statemachine.entities["statemachine.state2"]
        self.assertEqual(state2.name, "STATE2")
        self.assertEqual(state2.type, StateType.SIMPLE)
        self.assertTrue(state2 is region2.states[0])

    def test_transition_within_region(self):
        """Test a parse tree with a simple transition"""
        # Construct tree
        parse_tree = ParseTree()
        declarations_node = parse_tree.root_node.make_child(
            Token(TokenType.declarations)
        )
        state1_declaration = declarations_node.make_child(
            Token(TokenType.state_declaration)
        )
        state1_declaration.make_child(Token(TokenType.KEYWORD_STATE))
        state1_declaration.make_child(Token(TokenType.NAME, 0, 0, "STATE1"))

        state2_declaration = declarations_node.make_child(
            Token(TokenType.state_declaration)
        )
        state2_declaration.make_child(Token(TokenType.KEYWORD_STATE))
        state2_declaration.make_child(Token(TokenType.NAME, 0, 0, "STATE2"))

        transition1_declaration = declarations_node.make_child(
            Token(TokenType.transition_declaration)
        )
        transition1_declaration.make_child(Token(TokenType.NAME, 0, 0, "STATE1"))
        transition1_declaration.make_child(Token(TokenType.ARROW))
        transition1_declaration.make_child(Token(TokenType.NAME, 0, 0, "STATE2"))
        transition1_declaration.make_child(Token(TokenType.STEREOTYPE_ANY, 0, 0, "<<stereotype>>"))

        # Generate statemachine
        factory = ModelFactory()
        statemachine = factory.new_statemachine(parse_tree)

        # Assert
        state1 = statemachine.region.states[0]
        state2 = statemachine.region.states[1]
        transition1 = statemachine.region.transitions[0]
        self.assertEqual(transition1.source, state1)
        self.assertEqual(transition1.target, state2)
        self.assertEqual(transition1.stereotype, "stereotype")
        self.assertIsNone(transition1.trigger)
        self.assertIsNone(transition1.guard)
        self.assertIsNone(transition1.action)

        self.assertEqual(len(state1.outgoing_transitions), 1)
        self.assertEqual(state1.outgoing_transitions[0], transition1)
        self.assertEqual(len(state2.incoming_transitions), 1)
        self.assertEqual(state2.incoming_transitions[0], transition1)

if __name__ == "__main__":
    unittest.main()
