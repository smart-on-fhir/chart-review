"""Tests for commands/disagreements.py"""

import tempfile

from chart_review import common
from tests import base


class TestDisagreements(base.TestCase):
    @staticmethod
    def make_simple_export(tmpdir: str) -> None:
        common.write_json(
            f"{tmpdir}/export.json",
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
                                            "frog",
                                            "chicken",
                                        ],
                                    },
                                },
                            ],
                        },
                        {
                            "completed_by": 2,
                            "result": [
                                {
                                    "value": {
                                        "labels": [
                                            "frog",
                                            "horse",
                                            "ant",
                                        ],
                                    },
                                },
                            ],
                        },
                    ],
                    "data": {
                        "encounter_id": "enc",
                        "anon_encounter_id": "anon-enc",
                        "docref_mappings": {
                            "DiagnosticReport/dx": "DiagnosticReport/anon-dx",
                            "DocumentReference/doc": "anon-doc",
                        },
                    },
                },
                {  # another chart, without mappings (just to test output in that case)
                    "id": 2,
                    "annotations": [
                        {
                            "completed_by": 1,
                            "result": [
                                {
                                    "value": {
                                        "labels": [
                                            "ant",
                                        ],
                                    },
                                },
                            ],
                        },
                        {
                            "completed_by": 2,
                            "result": [{"value": {"labels": []}}],
                        },
                    ],
                },
                {  # another chart, annotated by a third annotator, should be ignored
                    "id": 3,
                    "annotations": [
                        {
                            "completed_by": 42,
                            "result": [
                                {
                                    "value": {
                                        "labels": [
                                            "elephant",
                                        ],
                                    },
                                },
                            ],
                        },
                    ],
                },
            ],
        )

    def test_disagreements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.make_simple_export(tmpdir)
            stdout = self.run_cli("disagreements", "1", "2", path=tmpdir)

        self.assertEqual(
            [
                "Comparing 2 charts (1–2)",
                "Truth: 1",
                "Annotator: 2",
                "",
                "╭──────────┬─────────┬────────────────╮",
                "│ Chart ID │ Label   │ Classification │",
                "├──────────┼─────────┼────────────────┤",
                "│ 1        │ ant     │ FP             │",
                "│ 1        │ chicken │ FN             │",
                "│ 1        │ horse   │ FP             │",
                "├──────────┼─────────┼────────────────┤",
                "│ 2        │ ant     │ FN             │",
                "╰──────────┴─────────┴────────────────╯",
            ],
            stdout.splitlines(),
        )

    def test_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.make_simple_export(tmpdir)
            stdout = self.run_cli("disagreements", "--csv", "1", "2", path=tmpdir)

        self.assertEqual(
            [
                "chart_id,label,classification",
                "1,ant,FP",
                "1,chicken,FN",
                "1,horse,FP",
                "2,ant,FN",
            ],
            stdout.splitlines(),
        )

    def test_with_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.make_simple_export(tmpdir)
            stdout = self.run_cli("disagreements", "--with-ids", "1", "2", path=tmpdir)

        self.assertEqual(
            [
                "Comparing 2 charts (1–2)",
                "Truth: 1",
                "Annotator: 2",
                "",
                "╭──────────┬───────────────────┬────────────────────┬─────────┬────────────────╮",
                "│ Chart ID │ FHIR ID           │ Anon ID            │ Label   │ Classification │",
                "├──────────┼───────────────────┼────────────────────┼─────────┼────────────────┤",
                "│ 1        │ Encounter/enc     │ Encounter/anon-enc │ ant     │ FP             │",
                "│ 1        │ DiagnosticReport/ │ DiagnosticReport/a │ ant     │ FP             │",
                "│          │ dx                │ non-dx             │         │                │",
                "│ 1        │ DocumentReference │ DocumentReference/ │ ant     │ FP             │",
                "│          │ /doc              │ anon-doc           │         │                │",
                "│ 1        │ Encounter/enc     │ Encounter/anon-enc │ chicken │ FN             │",
                "│ 1        │ DiagnosticReport/ │ DiagnosticReport/a │ chicken │ FN             │",
                "│          │ dx                │ non-dx             │         │                │",
                "│ 1        │ DocumentReference │ DocumentReference/ │ chicken │ FN             │",
                "│          │ /doc              │ anon-doc           │         │                │",
                "│ 1        │ Encounter/enc     │ Encounter/anon-enc │ horse   │ FP             │",
                "│ 1        │ DiagnosticReport/ │ DiagnosticReport/a │ horse   │ FP             │",
                "│          │ dx                │ non-dx             │         │                │",
                "│ 1        │ DocumentReference │ DocumentReference/ │ horse   │ FP             │",
                "│          │ /doc              │ anon-doc           │         │                │",
                "├──────────┼───────────────────┼────────────────────┼─────────┼────────────────┤",
                "│ 2        │                   │                    │ ant     │ FN             │",
                "╰──────────┴───────────────────┴────────────────────┴─────────┴────────────────╯",
            ],
            stdout.splitlines(),
        )

    def test_with_ids_cvs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.make_simple_export(tmpdir)
            stdout = self.run_cli("disagreements", "--with-ids", "--csv", "1", "2", path=tmpdir)

        self.assertEqual(
            [
                "chart_id,fhir_id,anon_id,label,classification",
                "1,Encounter/enc,Encounter/anon-enc,ant,FP",
                "1,DiagnosticReport/dx,DiagnosticReport/anon-dx,ant,FP",
                "1,DocumentReference/doc,DocumentReference/anon-doc,ant,FP",
                "1,Encounter/enc,Encounter/anon-enc,chicken,FN",
                "1,DiagnosticReport/dx,DiagnosticReport/anon-dx,chicken,FN",
                "1,DocumentReference/doc,DocumentReference/anon-doc,chicken,FN",
                "1,Encounter/enc,Encounter/anon-enc,horse,FP",
                "1,DiagnosticReport/dx,DiagnosticReport/anon-dx,horse,FP",
                "1,DocumentReference/doc,DocumentReference/anon-doc,horse,FP",
                "2,,,ant,FN",
            ],
            stdout.splitlines(),
        )

    def test_bad_annotator(self):
        # Truth
        with self.capture_stderr() as stderr:
            with self.assertRaises(SystemExit):
                with tempfile.TemporaryDirectory() as tmpdir:
                    self.make_simple_export(tmpdir)
                    self.run_cli("disagreements", "nope1", "2", path=tmpdir)
        self.assertEqual("Unrecognized annotator 'nope1'\n", stderr.getvalue())

        # Annotator
        with self.capture_stderr() as stderr:
            with self.assertRaises(SystemExit):
                with tempfile.TemporaryDirectory() as tmpdir:
                    self.make_simple_export(tmpdir)
                    self.run_cli("disagreements", "1", "nope2", path=tmpdir)
        self.assertEqual("Unrecognized annotator 'nope2'\n", stderr.getvalue())

    def test_same_annotators(self):
        with self.capture_stderr() as stderr:
            with self.assertRaises(SystemExit):
                with tempfile.TemporaryDirectory() as tmpdir:
                    self.make_simple_export(tmpdir)
                    self.run_cli("disagreements", "1", "1", path=tmpdir)
        self.assertEqual("Can’t compare the same annotator with themselves.\n", stderr.getvalue())
