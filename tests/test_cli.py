"""Tests for cli.py"""

import shutil
import tempfile

import chart_review
from chart_review import cli, common, errors
from tests import base


class TestCommandLine(base.TestCase):
    """Test case for the CLI entry point"""

    def assert_cold_output(self, output):
        self.assertEqual(
            """╭───────────┬─────────────┬───────────╮
│ Annotator │ Chart Count │ Chart IDs │
├───────────┼─────────────┼───────────┤
│ jane      │ 3           │ 1, 3–4    │
│ jill      │ 4           │ 1–4       │
│ john      │ 3           │ 1–2, 4    │
╰───────────┴─────────────┴───────────╯

Pass --help to see more options.
""",
            output,
        )

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

    def test_default_info(self):
        stdout = self.run_cli(path=f"{self.DATA_DIR}/cold")
        self.assert_cold_output(stdout)

    def test_default_info_ignored(self):
        stdout = self.run_cli(path=f"{self.DATA_DIR}/ignore")

        self.assertEqual(
            """╭───────────┬─────────────┬───────────╮
│ Annotator │ Chart Count │ Chart IDs │
├───────────┼─────────────┼───────────┤
│ adam      │ 2           │ 1–2       │
│ allison   │ 2           │ 1–2       │
╰───────────┴─────────────┴───────────╯
  Ignoring 3 charts (3–5)

Pass --help to see more options.
""",
            stdout,
        )

    def test_custom_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(f"{self.DATA_DIR}/cold/labelstudio-export.json", tmpdir)
            # mostly confirm it doesn't just error out
            stdout = self.run_cli(f"--config={self.DATA_DIR}/cold/config.yaml", path=tmpdir)
            self.assert_cold_output(stdout)

    def test_missing_config(self):
        """Still works, just with rough defaults"""
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(f"{self.DATA_DIR}/cold/labelstudio-export.json", tmpdir)
            stdout = self.run_cli(path=tmpdir)

            self.assertEqual(
                """╭───────────┬─────────────┬───────────╮
│ Annotator │ Chart Count │ Chart IDs │
├───────────┼─────────────┼───────────┤
│ 3         │ 4           │ 1–4       │
│ 5         │ 3           │ 1–2, 4    │
│ 6         │ 4           │ 1–4       │
╰───────────┴─────────────┴───────────╯

Pass --help to see more options.
""",
                stdout,
            )

    def test_bad_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(f"{self.DATA_DIR}/cold/labelstudio-export.json", tmpdir)
            common.write_text(f"{tmpdir}/config.json", "[1, 2]")
            with self.assertRaises(SystemExit) as cm:
                self.run_cli(path=tmpdir)
        self.assertEqual(cm.exception.code, errors.ERROR_INVALID_PROJECT)

    def test_missing_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(f"{tmpdir}/config.yaml", {"annotators": {"me": 1}})
            with self.assertRaises(SystemExit) as cm:
                self.run_cli(path=tmpdir)
        self.assertEqual(cm.exception.code, errors.ERROR_INVALID_PROJECT)
