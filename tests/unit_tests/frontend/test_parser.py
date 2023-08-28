import unittest
from textwrap import dedent

from tests.utilities import TestCaseBase

from gen_statemachine.frontend.tokens import TokenType
from gen_statemachine.frontend.parser import Parser


class TestParser(TestCaseBase):
    def test_basic_state_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 2)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")

    def test_state_declaration_with_label(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.LABEL)
        self.assertEqual(node.children[2].token.text, "hello world")

    def test_state_declaration_with_stereotype(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml
            
        state STATE1 <<stereotype>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[2].token.text, "<<stereotype>>")

    def test_state_declaration_with_label_and_stereotype(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 <<stereotype>> : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[2].token.text, "<<stereotype>>")
        self.assertEqual(node.children[3].token.type, TokenType.LABEL)
        self.assertEqual(node.children[3].token.text, "hello world")

    def test_note_declaration_left_of(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        note left of STATE1 : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.anchored_note_declaration)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_NOTE)
        self.assertEqual(node.children[1].token.type, TokenType.KEYWORD_LEFT_OF)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE1")
        self.assertEqual(node.children[3].token.type, TokenType.LABEL)
        self.assertEqual(node.children[3].token.text, "hello world")

    def test_note_declaration_right_of(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        note right of STATE1 : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.anchored_note_declaration)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_NOTE)
        self.assertEqual(node.children[1].token.type, TokenType.KEYWORD_RIGHT_OF)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE1")
        self.assertEqual(node.children[3].token.type, TokenType.LABEL)
        self.assertEqual(node.children[3].token.text, "hello world")

    def test_note_declaration_left_of_multiline(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        note left of STATE1
            hello
            world
        end note

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.anchored_note_declaration)
        self.assertEqual(len(node.children), 7)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_NOTE)
        self.assertEqual(node.children[1].token.type, TokenType.KEYWORD_LEFT_OF)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE1")
        self.assertEqual(node.children[3].token.type, TokenType.LABEL)
        self.assertEqual(node.children[3].token.text, "hello")
        self.assertEqual(node.children[4].token.type, TokenType.LABEL)
        self.assertEqual(node.children[4].token.text, "world")
        self.assertEqual(node.children[5].token.type, TokenType.KEYWORD_END)
        self.assertEqual(node.children[6].token.type, TokenType.KEYWORD_NOTE)

    def test_note_declaration_right_of_multiline(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        note right of STATE1
            hello
            world
        end note

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.anchored_note_declaration)
        self.assertEqual(len(node.children), 7)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_NOTE)
        self.assertEqual(node.children[1].token.type, TokenType.KEYWORD_RIGHT_OF)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE1")
        self.assertEqual(node.children[3].token.type, TokenType.LABEL)
        self.assertEqual(node.children[3].token.text, "hello")
        self.assertEqual(node.children[4].token.type, TokenType.LABEL)
        self.assertEqual(node.children[4].token.text, "world")
        self.assertEqual(node.children[5].token.type, TokenType.KEYWORD_END)
        self.assertEqual(node.children[6].token.type, TokenType.KEYWORD_NOTE)

    def test_floating_note_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        note "hello world" as NOTE1

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.floating_note_declaration)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_NOTE)
        self.assertEqual(node.children[1].token.type, TokenType.LABEL)
        self.assertEqual(node.children[1].token.text, "hello world")
        self.assertEqual(node.children[2].token.type, TokenType.KEYWORD_AS)
        self.assertEqual(node.children[3].token.type, TokenType.NAME)
        self.assertEqual(node.children[3].token.text, "NOTE1")

    def test_state_alias(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state "hello world" as STATE1

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_alias_declaration)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.LABEL)
        self.assertEqual(node.children[1].token.text, "hello world")
        self.assertEqual(node.children[2].token.type, TokenType.KEYWORD_AS)
        self.assertEqual(node.children[3].token.type, TokenType.NAME)
        self.assertEqual(node.children[3].token.text, "STATE1")

    def test_state_alias_with_stereotype(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state "hello world" as STATE1 <<stereotype>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_alias_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.LABEL)
        self.assertEqual(node.children[1].token.text, "hello world")
        self.assertEqual(node.children[2].token.type, TokenType.KEYWORD_AS)
        self.assertEqual(node.children[3].token.type, TokenType.NAME)
        self.assertEqual(node.children[3].token.text, "STATE1")
        self.assertEqual(node.children[4].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[4].token.text, "<<stereotype>>")

    def test_state_alias_with_label(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state "hello world" as STATE1 : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_alias_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.LABEL)
        self.assertEqual(node.children[1].token.text, "hello world")
        self.assertEqual(node.children[2].token.type, TokenType.KEYWORD_AS)
        self.assertEqual(node.children[3].token.type, TokenType.NAME)
        self.assertEqual(node.children[3].token.text, "STATE1")
        self.assertEqual(node.children[4].token.type, TokenType.LABEL)
        self.assertEqual(node.children[4].token.text, "hello world")

    def test_state_alias_with_label_and_stereotype(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state "hello world" as STATE1 <<stereotype>> : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_alias_declaration)
        self.assertEqual(len(node.children), 6)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.LABEL)
        self.assertEqual(node.children[1].token.text, "hello world")
        self.assertEqual(node.children[2].token.type, TokenType.KEYWORD_AS)
        self.assertEqual(node.children[3].token.type, TokenType.NAME)
        self.assertEqual(node.children[3].token.text, "STATE1")
        self.assertEqual(node.children[4].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[4].token.text, "<<stereotype>>")
        self.assertEqual(node.children[5].token.type, TokenType.LABEL)
        self.assertEqual(node.children[5].token.text, "hello world")

    def test_composite_state_alias_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state "hello world" as STATE1 <<stereotype>> {
            state STATE2
            [*] --> STATE1 : hello world
            STATE2 : label
        }

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_alias_declaration)
        self.assertEqual(len(node.children), 6)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.LABEL)
        self.assertEqual(node.children[1].token.text, "hello world")
        self.assertEqual(node.children[2].token.type, TokenType.KEYWORD_AS)
        self.assertEqual(node.children[3].token.type, TokenType.NAME)
        self.assertEqual(node.children[3].token.text, "STATE1")
        self.assertEqual(node.children[4].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[4].token.text, "<<stereotype>>")
        self.assertEqual(node.children[5].token.type, TokenType.declarations)
        nested_declarations_node = node.children[5]
        # Test nested state
        child_node = nested_declarations_node.children[0]
        self.assertEqual(len(child_node.children), 2)
        self.assertEqual(child_node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(child_node.children[1].token.type, TokenType.NAME)
        self.assertEqual(child_node.children[1].token.text, "STATE2")
        # Test nested transition
        child_node = nested_declarations_node.children[1]
        self.assertEqual(len(child_node.children), 5)
        self.assertEqual(
            child_node.children[0].token.type, TokenType.INITIAL_FINAL_STATE
        )
        self.assertEqual(child_node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(child_node.children[2].token.type, TokenType.NAME)
        self.assertEqual(child_node.children[2].token.text, "STATE1")
        self.assertEqual(child_node.children[3].token.type, TokenType.COLON)
        self.assertEqual(child_node.children[4].token.type, TokenType.transition_label)
        # Test nested state label
        child_node = nested_declarations_node.children[2]
        self.assertEqual(len(child_node.children), 3)
        self.assertEqual(child_node.children[0].token.type, TokenType.NAME)
        self.assertEqual(child_node.children[0].token.text, "STATE2")
        self.assertEqual(child_node.children[1].token.type, TokenType.COLON)
        self.assertEqual(child_node.children[2].token.type, TokenType.LABEL)

    def test_composite_state_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 <<stereotype>> {
            state STATE2
            [*] --> STATE1 : hello world
            STATE2 : label
        }

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[2].token.text, "<<stereotype>>")
        self.assertEqual(node.children[3].token.type, TokenType.declarations)
        nested_declarations_node = node.children[3]
        # Test nested state
        child_node = nested_declarations_node.children[0]
        self.assertEqual(len(child_node.children), 2)
        self.assertEqual(child_node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(child_node.children[1].token.type, TokenType.NAME)
        self.assertEqual(child_node.children[1].token.text, "STATE2")
        # Test nested transition
        child_node = nested_declarations_node.children[1]
        self.assertEqual(len(child_node.children), 5)
        self.assertEqual(
            child_node.children[0].token.type, TokenType.INITIAL_FINAL_STATE
        )
        self.assertEqual(child_node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(child_node.children[2].token.type, TokenType.NAME)
        self.assertEqual(child_node.children[2].token.text, "STATE1")
        self.assertEqual(child_node.children[3].token.type, TokenType.COLON)
        self.assertEqual(child_node.children[4].token.type, TokenType.transition_label)
        # Test nested state label
        child_node = nested_declarations_node.children[2]
        self.assertEqual(len(child_node.children), 3)
        self.assertEqual(child_node.children[0].token.type, TokenType.NAME)
        self.assertEqual(child_node.children[0].token.text, "STATE2")
        self.assertEqual(child_node.children[1].token.type, TokenType.COLON)
        self.assertEqual(child_node.children[2].token.type, TokenType.LABEL)
        self.assertEqual(child_node.children[2].token.text, "label")

    def test_state_transition_from_entry(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        [*] --> STATE1

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.INITIAL_FINAL_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE1")

    def test_state_transition_from_entry_with_stereotype(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        [*] --> STATE1 <<stereotype>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.INITIAL_FINAL_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE1")
        self.assertEqual(node.children[3].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[3].token.text, "<<stereotype>>")

    def test_state_transition_from_entry_with_label(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        [*] --> STATE1 : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[0].token.type, TokenType.INITIAL_FINAL_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE1")
        self.assertEqual(node.children[3].token.type, TokenType.COLON)
        label_node = node.children[4]
        self.assertEqual(len(label_node.children), 1)
        self.assertEqual(label_node.children[0].token.type, TokenType.TRIGGER)
        self.assertEqual(label_node.children[0].token.text, "hello world")

    def test_state_transition_from_entry_with_label_and_stereotype(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        [*] --> STATE1 <<stereotype>> : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 6)
        self.assertEqual(node.children[0].token.type, TokenType.INITIAL_FINAL_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE1")
        self.assertEqual(node.children[3].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[3].token.text, "<<stereotype>>")
        self.assertEqual(node.children[4].token.type, TokenType.COLON)
        label_node = node.children[5]
        self.assertEqual(len(label_node.children), 1)
        self.assertEqual(label_node.children[0].token.type, TokenType.TRIGGER)
        self.assertEqual(label_node.children[0].token.text, "hello world")

    def test_state_transition_to_entry(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> [*]

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.INITIAL_FINAL_STATE)

    def test_state_transition_to_entry_with_stereotype(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> [*] <<stereotype>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.INITIAL_FINAL_STATE)
        self.assertEqual(node.children[3].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[3].token.text, "<<stereotype>>")

    def test_state_transition_to_entry_with_label(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> [*] : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.INITIAL_FINAL_STATE)
        self.assertEqual(node.children[3].token.type, TokenType.COLON)
        label_node = node.children[4]
        self.assertEqual(len(label_node.children), 1)
        self.assertEqual(label_node.children[0].token.type, TokenType.TRIGGER)
        self.assertEqual(label_node.children[0].token.text, "hello world")

    def test_state_transition_to_entry_with_label_and_stereotype(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> [*] <<stereotype>> : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 6)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.INITIAL_FINAL_STATE)
        self.assertEqual(node.children[3].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[3].token.text, "<<stereotype>>")
        self.assertEqual(node.children[4].token.type, TokenType.COLON)
        label_node = node.children[5]
        self.assertEqual(len(label_node.children), 1)
        self.assertEqual(label_node.children[0].token.type, TokenType.TRIGGER)
        self.assertEqual(label_node.children[0].token.text, "hello world")

    def test_state_transition(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> STATE2

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE2")

    def test_state_transition_with_stereotype(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> STATE2 <<stereotype>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE2")
        self.assertEqual(node.children[3].token.type, TokenType.STEREOTYPE_ANY)
        self.assertEqual(node.children[3].token.text, "<<stereotype>>")

    def test_state_transition_label_with_trigger(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> STATE2 : hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE2")
        self.assertEqual(node.children[3].token.type, TokenType.COLON)
        label_node = node.children[4]
        self.assertEqual(len(label_node.children), 1)
        self.assertEqual(label_node.children[0].token.type, TokenType.TRIGGER)
        self.assertEqual(label_node.children[0].token.text, "hello world")

    def test_state_transition_label_with_guard(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> STATE2 : [Hulk > Thor]

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE2")
        self.assertEqual(node.children[3].token.type, TokenType.COLON)
        label_node = node.children[4]
        self.assertEqual(len(label_node.children), 3)
        self.assertEqual(label_node.children[0].token.type, TokenType.OPEN_SQ_BRACKET)
        self.assertEqual(label_node.children[1].token.type, TokenType.GUARD)
        self.assertEqual(label_node.children[1].token.text, "Hulk > Thor")
        self.assertEqual(label_node.children[2].token.type, TokenType.CLOSE_SQ_BRACKET)

    def test_state_transition_label_with_behavior(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> STATE2 : /do_something();
        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE2")
        self.assertEqual(node.children[3].token.type, TokenType.COLON)
        label_node = node.children[4]
        self.assertEqual(len(label_node.children), 2)
        self.assertEqual(label_node.children[0].token.type, TokenType.FORWARD_SLASH)
        self.assertEqual(label_node.children[1].token.type, TokenType.BEHAVIOR)
        self.assertEqual(label_node.children[1].token.text, "do_something();")

    def test_full_state_transition_label(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 --> STATE2 : evDoSomething[Hulk > Thor] / do_something();

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.transition_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[0].token.type, TokenType.NAME)
        self.assertEqual(node.children[0].token.text, "STATE1")
        self.assertEqual(node.children[1].token.type, TokenType.ARROW)
        self.assertEqual(node.children[2].token.type, TokenType.NAME)
        self.assertEqual(node.children[2].token.text, "STATE2")
        self.assertEqual(node.children[3].token.type, TokenType.COLON)
        label_node = node.children[4]
        self.assertEqual(len(label_node.children), 6)
        self.assertEqual(label_node.children[0].token.type, TokenType.TRIGGER)
        self.assertEqual(label_node.children[0].token.text, "evDoSomething")
        self.assertEqual(label_node.children[1].token.type, TokenType.OPEN_SQ_BRACKET)
        self.assertEqual(label_node.children[2].token.type, TokenType.GUARD)
        self.assertEqual(label_node.children[2].token.text, "Hulk > Thor")
        self.assertEqual(label_node.children[3].token.type, TokenType.CLOSE_SQ_BRACKET)
        self.assertEqual(label_node.children[4].token.type, TokenType.FORWARD_SLASH)
        self.assertEqual(label_node.children[5].token.type, TokenType.BEHAVIOR)
        self.assertEqual(label_node.children[5].token.text, "do_something();")

    def test_choice_state_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 <<choice>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.STEREOTYPE_CHOICE)

    def test_entry_point_state_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 <<entryPoint>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.STEREOTYPE_ENTRY_POINT)

    def test_exit_point_state_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 <<exitPoint>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.STEREOTYPE_EXIT_POINT)

    def test_input_pin_state_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 <<inputPin>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.STEREOTYPE_INPUT_PIN)

    def test_output_pin_state_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 <<outputPin>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.STEREOTYPE_OUTPUT_PIN)

    def test_expansion_input_state_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 <<expansionInput>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(
            node.children[2].token.type, TokenType.STEREOTYPE_EXPANSION_INPUT
        )

    def test_expansion_output_state_declaration(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 <<expansionOutput>>

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(
            node.children[2].token.type, TokenType.STEREOTYPE_EXPANSION_OUTPUT
        )

    def test_line_comment(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        'hello world

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.comment)
        self.assertEqual(len(node.children), 2)
        self.assertEqual(node.children[0].token.type, TokenType.APOSTROPHE)
        self.assertEqual(node.children[1].token.type, TokenType.LABEL)
        self.assertEqual(node.children[1].token.text, "hello world")

    def test_single_line_block_comment(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        /'    hello world'/

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.comment)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.START_BLOCK_COMMENT)
        self.assertEqual(node.children[1].token.type, TokenType.LABEL)
        self.assertEqual(node.children[1].token.text, "hello world")
        self.assertEqual(node.children[2].token.type, TokenType.END_BLOCK_COMMENT)

    def test_multi_line_block_comment(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        /' hello
        
        world
        
        '/

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.comment)
        self.assertEqual(len(node.children), 4)
        self.assertEqual(node.children[0].token.type, TokenType.START_BLOCK_COMMENT)
        self.assertEqual(node.children[1].token.type, TokenType.LABEL)
        self.assertEqual(node.children[1].token.text, "hello")
        self.assertEqual(node.children[2].token.type, TokenType.LABEL)
        self.assertEqual(node.children[2].token.text, "world")
        self.assertEqual(node.children[3].token.type, TokenType.END_BLOCK_COMMENT)

    def test_state_declaration_with_entry_action(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 : entry  / doSomething();

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.entry_action)
        action_node = node.children[2]
        self.assertEqual(len(action_node.children), 3)
        self.assertEqual(action_node.children[0].token.type, TokenType.KEYWORD_ENTRY)
        self.assertEqual(action_node.children[2].token.type, TokenType.BEHAVIOR)
        self.assertEqual(action_node.children[2].token.text, "doSomething();")

    def test_state_declaration_with_exit_action(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state STATE1 : exit/ doSomething();

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_declaration)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[0].token.type, TokenType.KEYWORD_STATE)
        self.assertEqual(node.children[1].token.type, TokenType.NAME)
        self.assertEqual(node.children[1].token.text, "STATE1")
        self.assertEqual(node.children[2].token.type, TokenType.exit_action)
        action_node = node.children[2]
        self.assertEqual(len(action_node.children), 3)
        self.assertEqual(action_node.children[0].token.type, TokenType.KEYWORD_EXIT)
        self.assertEqual(action_node.children[2].token.type, TokenType.BEHAVIOR)
        self.assertEqual(action_node.children[2].token.text, "doSomething();")

    def test_state_alias_declaration_with_entry_action(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state "state 1" as STATE1 : entry  / doSomething();

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_alias_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[4].token.type, TokenType.entry_action)
        action_node = node.children[4]
        self.assertEqual(len(action_node.children), 3)
        self.assertEqual(action_node.children[0].token.type, TokenType.KEYWORD_ENTRY)
        self.assertEqual(action_node.children[2].token.type, TokenType.BEHAVIOR)
        self.assertEqual(action_node.children[2].token.text, "doSomething();")

    def test_state_alias_declaration_with_exit_action(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        state "state 1" as STATE1 : exit  / doSomething();

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_alias_declaration)
        self.assertEqual(len(node.children), 5)
        self.assertEqual(node.children[4].token.type, TokenType.exit_action)
        action_node = node.children[4]
        self.assertEqual(len(action_node.children), 3)
        self.assertEqual(action_node.children[0].token.type, TokenType.KEYWORD_EXIT)
        self.assertEqual(action_node.children[2].token.type, TokenType.BEHAVIOR)
        self.assertEqual(action_node.children[2].token.text, "doSomething();")

    def test_state_label_with_entry_action(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 : entry/ doSomething();

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_label)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[2].token.type, TokenType.entry_action)
        action_node = node.children[2]
        self.assertEqual(len(action_node.children), 3)
        self.assertEqual(action_node.children[0].token.type, TokenType.KEYWORD_ENTRY)
        self.assertEqual(action_node.children[2].token.type, TokenType.BEHAVIOR)
        self.assertEqual(action_node.children[2].token.text, "doSomething();")

    def test_state_label_with_exit_action(self):
        file_path = self.create_file(
            contents=dedent(
                """
        @startuml

        STATE1 : exit   / doSomething();

        @enduml
        """
            )
        )
        parser = Parser()

        with open(file_path, "r") as file:
            parse_tree = parser.parse_puml(file)

        declarations_node = parse_tree.root_node.children[1]
        node = declarations_node.children[0]
        self.assertEqual(node.token.type, TokenType.state_label)
        self.assertEqual(len(node.children), 3)
        self.assertEqual(node.children[2].token.type, TokenType.exit_action)
        action_node = node.children[2]
        self.assertEqual(len(action_node.children), 3)
        self.assertEqual(action_node.children[0].token.type, TokenType.KEYWORD_EXIT)
        self.assertEqual(action_node.children[2].token.type, TokenType.BEHAVIOR)
        self.assertEqual(action_node.children[2].token.text, "doSomething();")
