from tests.utilities import TestCaseBase
from textwrap import dedent
from gen_statemachine.model import StateMachine, ModelBuilder
from gen_statemachine.frontend import Parser


class FrontEndTestCase(TestCaseBase):
    def setUp(self):
        super().setUp()
        self.parser = Parser()
        self.model_builder = ModelBuilder()

    def generate_model(self, puml: str) -> StateMachine:
        file_name = "test.file"
        file = self.create_file(file_name=file_name, contents=dedent(puml))

        with open(file_name, "r") as file:
            parse_tree = self.parser.parse_puml(file)

        statemachine_model = self.model_builder.build(parse_tree)
        return statemachine_model
