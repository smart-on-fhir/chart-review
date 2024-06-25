"""Tests for commands/labels.py"""

import tempfile

from chart_review import common
from tests import base


class TestLabels(base.TestCase):
    """Test case for the top-level labels code"""

    def test_labels(self):
        stdout = self.run_cli("labels", path=f"{self.DATA_DIR}/cold")

        self.assertEqual(
            """╭───────────┬──────────┬─────────────╮
│ Annotator │ Label    │ Chart Count │
├───────────┼──────────┼─────────────┤
│ Any       │ Cough    │ 2           │
│ Any       │ Fatigue  │ 3           │
│ Any       │ Headache │ 3           │
├───────────┼──────────┼─────────────┤
│ jane      │ Cough    │ 1           │
│ jane      │ Fatigue  │ 2           │
│ jane      │ Headache │ 2           │
├───────────┼──────────┼─────────────┤
│ jill      │ Cough    │ 2           │
│ jill      │ Fatigue  │ 3           │
│ jill      │ Headache │ 0           │
├───────────┼──────────┼─────────────┤
│ john      │ Cough    │ 1           │
│ john      │ Fatigue  │ 2           │
│ john      │ Headache │ 2           │
╰───────────┴──────────┴─────────────╯
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
            stdout = self.run_cli("labels", path=tmpdir)

        self.assertEqual(
            """╭───────────┬──────────┬─────────────╮
│ Annotator │ Label    │ Chart Count │
├───────────┼──────────┼─────────────┤
│ Any       │ recent   │ 0           │
│ Any       │ symptoms │ 0           │
╰───────────┴──────────┴─────────────╯
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
            stdout = self.run_cli("labels", path=tmpdir)

        self.assertEqual(
            "Ignoring 3 charts (3–4, 6)",
            stdout.splitlines()[-1].strip(),
        )

    def test_labels_csv(self):
        """Verify that can print in CSV format"""
        stdout = self.run_cli("labels", "--csv", path=f"{self.DATA_DIR}/external")

        self.assertEqual(
            [
                "annotator,label,chart_count",
                "Any,happy,1",
                "Any,sad,1",
                "human,happy,1",
                "human,sad,1",
                "icd10-doc,happy,1",
                "icd10-doc,sad,1",
                "icd10-enc,happy,1",
                "icd10-enc,sad,1",
            ],
            stdout.splitlines(),
        )
