"""Tests for external.py"""

import tempfile

from chart_review import cohort, common, config
from tests import base


class TestExternal(base.TestCase):
    """Test case for basic external ID merging"""

    def test_basic_read(self):
        reader = cohort.CohortReader(config.ProjectConfig(f"{self.DATA_DIR}/external"))

        self.assertEqual(
            {
                "human": {
                    1: {base.Label("happy"), base.Label("sad")},
                    # This was a note that didn't appear in the icd10 external annotations
                    # (and also didn't have a positive label by the human reviewer).
                    # Just here to test that it didn't screw anything up.
                    2: set(),
                    # This was an external annotation that said "saw it,
                    # but no labels for this note"
                    3: set(),
                },
                "icd10-doc": {1: base.labels({"happy", "hungry", "sad", "tired"}), 3: set()},
                "icd10-enc": {1: base.labels({"happy", "hungry", "sad", "tired"}), 3: set()},
            },
            reader.annotations.mentions,
        )

        # Confirm ranges got auto-detected for both human and icd10
        self.assertEqual(
            {
                "human": {1, 2, 3},
                "icd10-doc": {1, 3},
                "icd10-enc": {1, 3},
            },
            reader.note_range,
        )

    def test_assumes_encounter_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json", {"annotators": {"ext": {"filename": "ext.csv"}}}
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {"id": 1, "data": {"enc_id": "could-be-either", "docref_mappings": {"a": "b"}}},
                    {"id": 2, "data": {"docref_mappings": {"could-be-either": "anon"}}},
                ],
            )
            common.write_text(f"{tmpdir}/ext.csv", "blarg,label\ncould-be-either,Confusing")
            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))

        self.assertEqual({"ext": {1}}, reader.note_range)

    def test_bad_annotator_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {"annotators": {"ext": "ext.csv"}},  # no filename:
            )
            common.write_json(f"{tmpdir}/labelstudio-export.json", [{"id": 1}])

            with self.assertRaisesRegex(ValueError, "^Did not understand config"):
                cohort.CohortReader(config.ProjectConfig(tmpdir))

    def test_missing_label_studio_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json", {"annotators": {"ext": {"filename": "ext.csv"}}}
            )
            common.write_json(f"{tmpdir}/labelstudio-export.json", [{"id": 1, "data": {}}])
            common.write_text(f"{tmpdir}/ext.csv", "blarg,label\nenc-id,Fever")

            with self.assertRaisesRegex(ValueError, "^Your Label Studio export does not include"):
                cohort.CohortReader(config.ProjectConfig(tmpdir))

    def test_sublabels_happy_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json", {"annotators": {"ext": {"filename": "ext.csv"}}}
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "data": {
                            "encounter_id": "enc",
                            "docref_mappings": {"DocumentReference/a": "DocumentReference/a_anon"},
                        },
                    },
                    {
                        "id": 2,
                        "data": {
                            "encounter_id": "enc",
                            "docref_mappings": {"DocumentReference/b": "DocumentReference/b_anon"},
                        },
                    },
                ],
            )
            common.write_text(
                f"{tmpdir}/ext.csv",
                """blarg,label,sublabel_name,sublabel_value,note_ref
                bogus,A,B,C,a
                bogus,,B,C,b""",  # empty 'label' col should give empty label set result
            )

            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))

        self.assertEqual(
            reader.annotations.mentions,
            {"ext": {1: base.labels({"A|B|C"}), 2: set()}},
        )

    def test_sublabels_no_id_col(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json", {"annotators": {"ext": {"filename": "ext.csv"}}}
            )
            common.write_json(f"{tmpdir}/labelstudio-export.json", [{"id": 1, "data": {}}])
            common.write_text(
                f"{tmpdir}/ext.csv",
                """blarg,label,sublabel_name,sublabel_value
                bogus,A,B,C""",
            )

            with self.assertRaisesRegex(ValueError, "no resource ID column found"):
                cohort.CohortReader(config.ProjectConfig(tmpdir))

    def test_sublabels_no_label_col(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json", {"annotators": {"ext": {"filename": "ext.csv"}}}
            )
            common.write_json(f"{tmpdir}/labelstudio-export.json", [{"id": 1, "data": {}}])
            common.write_text(
                f"{tmpdir}/ext.csv",
                """blarg,diagnosticreport_id,sublabel_name,sublabel_value
                bogus,id,B,C""",
            )

            with self.assertRaisesRegex(ValueError, "no 'label' column found"):
                cohort.CohortReader(config.ProjectConfig(tmpdir))

    def test_sublabels_no_sublabel_name_col(self):
        """This one works, you just can't specify sublabels, naturally"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json", {"annotators": {"ext": {"filename": "ext.csv"}}}
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "data": {
                            "encounter_id": "enc",
                            "docref_mappings": {"DiagnosticReport/a": "DiagnosticReport/a_anon"},
                        },
                    }
                ],
            )
            common.write_text(
                f"{tmpdir}/ext.csv",
                """blarg,diagnosticreport_id,label
                bogus,a,Label1""",
            )

            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))

        self.assertEqual(reader.annotations.mentions, {"ext": {1: base.labels({"Label1"})}})

    def test_sublabels_no_sublabel_value_col(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json", {"annotators": {"ext": {"filename": "ext.csv"}}}
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "data": {
                            "encounter_id": "enc",
                            "docref_mappings": {"DiagnosticReport/a": "DiagnosticReport/a_anon"},
                        },
                    }
                ],
            )
            common.write_text(
                f"{tmpdir}/ext.csv",
                """blarg,diagnosticreport_id,label,sublabel_name
                bogus,a,Label1,Sub1""",
            )

            with self.assertRaisesRegex(ValueError, "no 'sublabel_value' column found"):
                cohort.CohortReader(config.ProjectConfig(tmpdir))
