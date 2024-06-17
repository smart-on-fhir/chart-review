"""Tests for cli.py"""

import chart_review
from chart_review import cli
from tests import base


class TestCommandLine(base.TestCase):
    """Test case for the CLI entry point"""

    def test_version(self):
        # Manually capture stdout (rather than helper self.run_cli) because --version actually
        # exits the program, and we have to handle the exception rather than just grabbing the
        # return value which would be more convenient.
        with self.capture_stdout() as stdout:
            with self.assertRaises(SystemExit) as cm:
                cli.main_cli(["--version"])

        self.assertEqual(0, cm.exception.code)

        version = chart_review.__version__
        self.assertEqual(f"chart-review {version}\n", stdout.getvalue())
