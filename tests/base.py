"""Base class for tests"""

import contextlib
import io
import os
import unittest

from chart_review import cli


class TestCase(unittest.TestCase):
    """Test case parent class"""

    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    @staticmethod
    def run_cli(*args) -> str:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main_cli(list(args))
        return stdout.getvalue()
