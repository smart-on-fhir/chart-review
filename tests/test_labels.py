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

    def test_sublabels(self):
        output = self.run_cli("labels", path=f"{self.DATA_DIR}/sublabels")
        self.assertEqual(
            output,
            """╭───────────┬────────────────────────────────┬─────────────╮
│ Annotator │ Label                          │ Chart Count │
├───────────┼────────────────────────────────┼─────────────┤
│ Any       │ Deceased                       │ 1           │
│ Any       │ Deceased → False               │ 1           │
│ Any       │ Deceased → Datetime → 11/12/25 │ 1           │
│ Any       │ Deceased → Datetime → 11/13/25 │ 1           │
│ Any       │ Fungal → Confirmed             │ 1           │
│ Any       │ Infection                      │ 1           │
│ Any       │ Infection → Confirmed          │ 1           │
│ Any       │ Infection → Suspected          │ 1           │
├───────────┼────────────────────────────────┼─────────────┤
│ alice     │ Deceased                       │ 1           │
│ alice     │ Deceased → False               │ 1           │
│ alice     │ Deceased → Datetime → 11/12/25 │ 1           │
│ alice     │ Deceased → Datetime → 11/13/25 │ 0           │
│ alice     │ Fungal → Confirmed             │ 1           │
│ alice     │ Infection                      │ 0           │
│ alice     │ Infection → Confirmed          │ 0           │
│ alice     │ Infection → Suspected          │ 1           │
├───────────┼────────────────────────────────┼─────────────┤
│ bob       │ Deceased                       │ 0           │
│ bob       │ Deceased → False               │ 1           │
│ bob       │ Deceased → Datetime → 11/12/25 │ 0           │
│ bob       │ Deceased → Datetime → 11/13/25 │ 1           │
│ bob       │ Fungal → Confirmed             │ 1           │
│ bob       │ Infection                      │ 1           │
│ bob       │ Infection → Confirmed          │ 0           │
│ bob       │ Infection → Suspected          │ 1           │
├───────────┼────────────────────────────────┼─────────────┤
│ carla     │ Deceased                       │ 0           │
│ carla     │ Deceased → False               │ 1           │
│ carla     │ Deceased → Datetime → 11/12/25 │ 1           │
│ carla     │ Deceased → Datetime → 11/13/25 │ 0           │
│ carla     │ Fungal → Confirmed             │ 1           │
│ carla     │ Infection                      │ 0           │
│ carla     │ Infection → Confirmed          │ 1           │
│ carla     │ Infection → Suspected          │ 0           │
╰───────────┴────────────────────────────────┴─────────────╯
""",
        )
