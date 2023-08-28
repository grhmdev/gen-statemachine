from tests.end_to_end.test_case import EndToEndTestCase
from pathlib import Path
from unittest.mock import Mock, call


class T1_pass_through(EndToEndTestCase):
    def test(self):
        self.run_test()


class T2_composite_pass_through(EndToEndTestCase):
    def test(self):
        self.run_test()


class T3_nested_entry_exit(EndToEndTestCase):
    def test(self):
        self.run_test()


class T4_cross_region_entry_exit(EndToEndTestCase):
    def test(self):
        self.run_test()


class T5_event_pass_through(EndToEndTestCase):
    def test(self):
        self.run_test()


class T6_event_actions(EndToEndTestCase):
    def test(self):
        self.run_test()
