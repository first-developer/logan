

from unittest import TestCase
from logan.cli import sh
import sys

class TestLogan(TestCase):

    def setUp(self):pass


    # ------------------------------------------------------------------------------

    def test_it_should_be_able_to_show_help(self):

        log_file =

        return_code = sh("-h", output=sys.stdout)

        self.assertEqual(, 0, "Command execution failed")
