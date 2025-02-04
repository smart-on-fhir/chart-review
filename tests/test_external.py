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
                    1: {"happy", "sad"},
                    # This was a note that didn't appear in the icd10 external annotations
                    # (and also didn't have a positive label by the human reviewer).
                    # Just here to test that it didn't screw anything up.
                    2: set(),
                    # This was an external annotation that said "saw it,
                    # but no labels for this note"
                    3: set(),
                },
                "icd10-doc": {1: {"happy", "hungry", "sad", "tired"}, 3: set()},
                "icd10-enc": {1: {"happy", "hungry", "sad", "tired"}, 3: set()},
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
                    {"id": 1, "data": {"enc_id": "could-be-either", "docref_mappings": {}}},
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
