from tests.end_to_end import EndToEndTestCase
from pathlib import Path
from unittest.mock import Mock, call


class TestRegionEntryAndExit(EndToEndTestCase):
    def setUp(self):
        super().setUp(test_name=Path(__file__).stem)

    def test_region_entry_exit(self):
        self.run_program()
        generated_module = self.import_statemachine_module()

        sm = generated_module.Statemachine()
        sm.action = Mock()
        sm.start()

        expected_action_calls = [
            call("Entered State A"),
            call("Entered State B"),
            call("Exited State B"),
            call("Entered State C"),
            call("Exited State C"),
            call("Exited State A"),
        ]
        sm.action.assert_has_calls(expected_action_calls)
