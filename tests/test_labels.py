"""Tests for commands/labels.py"""

import tempfile

from chart_review import common
from tests import base


class TestLabels(base.TestCase):
    """Test case for the top-level labels code"""

    def test_labels(self):
        stdout = self.run_cli("--project-dir", f"{self.DATA_DIR}/cold", "labels")

        self.assertEqual(
            """╭───────────┬─────────────┬──────────╮
│ Annotator │ Chart Count │ Label    │
├───────────┼─────────────┼──────────┤
│ Any       │ 2           │ Cough    │
│ Any       │ 3           │ Fatigue  │
│ Any       │ 3           │ Headache │
├───────────┼─────────────┼──────────┤
│ jane      │ 1           │ Cough    │
│ jane      │ 2           │ Fatigue  │
│ jane      │ 2           │ Headache │
├───────────┼─────────────┼──────────┤
│ jill      │ 2           │ Cough    │
│ jill      │ 3           │ Fatigue  │
│ jill      │ 0           │ Headache │
├───────────┼─────────────┼──────────┤
│ john      │ 1           │ Cough    │
│ john      │ 2           │ Fatigue  │
│ john      │ 2           │ Headache │
╰───────────┴─────────────┴──────────╯
""",
            stdout,
        )

    def test_labels_grouped(self):
        """Verify that we only show final grouped labels, not intermediate ones"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {
                    "labels": ["fever", "rash", "recent"],
                    "grouped-labels": {"symptoms": ["fever", "rash"]},
                },
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [],
            )
            stdout = self.run_cli("labels", "--project-dir", tmpdir)

        self.assertEqual(
            """╭───────────┬─────────────┬──────────╮
│ Annotator │ Chart Count │ Label    │
├───────────┼─────────────┼──────────┤
│ Any       │ 0           │ recent   │
│ Any       │ 0           │ symptoms │
╰───────────┴─────────────┴──────────╯
""",
            stdout,
        )

    def test_labels_ignored(self):
        """Verify that we show info on ignored notes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {
                    "ignore": [3, 4, 6],
                },
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {"id": 3},
                    {"id": 4},
                    {"id": 5},
                    {"id": 6},
                ],
            )
            stdout = self.run_cli("labels", "--project-dir", tmpdir)

        self.assertEqual(
            "Ignoring 3 charts (3–4, 6)",
            stdout.splitlines()[-1].strip(),
        )
