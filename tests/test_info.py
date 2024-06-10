"""Tests for commands/info.py"""

import contextlib
import io
import os
import tempfile
import unittest

from chart_review import cli, common

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestInfo(unittest.TestCase):
    """Test case for the top-level info code"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    @staticmethod
    def grab_output(*args) -> str:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main_cli(["info", *args])
        return stdout.getvalue()

    def test_info(self):
        stdout = self.grab_output("--project-dir", f"{DATA_DIR}/cold")

        self.assertEqual(
            """╭───────────┬─────────────┬───────────╮
│ Annotator │ Chart Count │ Chart IDs │
├───────────┼─────────────┼───────────┤
│ jane      │ 3           │ 1, 3–4    │
│ jill      │ 4           │ 1–4       │
│ john      │ 3           │ 1–2, 4    │
╰───────────┴─────────────┴───────────╯
""",
            stdout,
        )

    def test_info_ignored(self):
        stdout = self.grab_output("--project-dir", f"{DATA_DIR}/ignore")

        self.assertEqual(
            """╭───────────┬─────────────┬───────────╮
│ Annotator │ Chart Count │ Chart IDs │
├───────────┼─────────────┼───────────┤
│ adam      │ 2           │ 1–2       │
│ allison   │ 2           │ 1–2       │
╰───────────┴─────────────┴───────────╯
  Ignoring 3 charts (3–5)
""",
            stdout,
        )

    def test_ids_quoted(self):
        """Verify that we quote the output when needed"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(f"{tmpdir}/config.json", {})
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "data": {
                            "enc_id": "Orig,\\ 'Enc",
                            "anon_id": 'Anon "Enc',
                        },
                    },
                ],
            )
            stdout = self.grab_output("--ids", "--project-dir", tmpdir)

        lines = stdout.splitlines()
        self.assertEqual(2, len(lines))
        self.assertEqual('1,"Encounter/Orig,\\ \'Enc","Encounter/Anon ""Enc"', lines[1])

    def test_ids_sources(self):
        """Verify that we pull IDs from all the places"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {
                    "annotators": {"carl": 1},
                },
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [
                                    {
                                        "value": {
                                            "labels": [
                                                "My Label",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                        # only orig encounter, no docref mappings
                        "data": {
                            "enc_id": "Orig",
                        },
                    },
                    {
                        "id": 2,
                        # only anon encounter, a single docref mapping
                        "data": {
                            "anon_id": "Anon",
                            "docref_mappings": {
                                "Orig": "Anon",
                            },
                        },
                    },
                    {
                        "id": 3,
                        # no encounter info, multiple docref mappings
                        "data": {
                            "docref_mappings": {
                                "Orig1": "Anon1",
                                "Orig2": "Anon2",
                            },
                        },
                    },
                    {
                        "id": 4,
                        # full encounter info, no docref mappings
                        "data": {
                            "enc_id": "a",
                            "anon_id": "b",
                        },
                    },
                    {
                        "id": 5,
                        # no metadata at all
                    },
                ],
            )
            stdout = self.grab_output("--ids", "--project-dir", tmpdir)

        self.assertEqual(
            [
                "chart_id,original_fhir_id,anonymized_fhir_id",
                "1,Encounter/Orig,",
                "2,,Encounter/Anon",
                "2,DocumentReference/Orig,DocumentReference/Anon",
                "3,DocumentReference/Orig1,DocumentReference/Anon1",
                "3,DocumentReference/Orig2,DocumentReference/Anon2",
                "4,Encounter/a,Encounter/b",
                "5,,",
            ],
            stdout.splitlines(),
        )

    def test_labels(self):
        stdout = self.grab_output("--project-dir", f"{DATA_DIR}/cold", "--labels")

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
            stdout = self.grab_output("--labels", "--project-dir", tmpdir)

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
            stdout = self.grab_output("--labels", "--project-dir", tmpdir)

        self.assertEqual(
            "Ignoring 3 charts (3–4, 6)",
            stdout.splitlines()[-1].strip(),
        )
