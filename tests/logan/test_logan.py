

from unittest import TestCase
from logan.cli import sh


class TestLogan(TestCase):

    def setUp(self):pass


    # ------------------------------------------------------------------------------

    def test_it_should_be_able_to_show_help(self):

        self.assertEqual(sh("-h"), 0, "Command execution failed")
