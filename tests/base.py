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
    def run_cli(*args, path: str) -> str:
        args = ["--project-dir", path, *args]
        with TestCase.capture_stdout() as stdout:
            cli.main_cli(args)
        return stdout.getvalue()

    @staticmethod
    @contextlib.contextmanager
    def capture_stdout() -> io.StringIO:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            yield stdout

    @staticmethod
    @contextlib.contextmanager
    def capture_stderr() -> io.StringIO:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            yield stderr
