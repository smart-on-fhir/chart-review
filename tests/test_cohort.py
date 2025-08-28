"""Tests for cohort.py"""

import tempfile

from chart_review import cohort, common, config
from tests import base


class TestCohort(base.TestCase):
    """Test case for basic cohort management"""

    def test_no_specified_label(self):
        """Verify that no label setup grabs all found labels from the export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {
                    "annotators": {"bob": 1, "alice": 2},
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
                                        "value": {"labels": ["Label A", "Label B"]},
                                    }
                                ],
                            },
                        ],
                    },
                ],
            )
            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))

        self.assertEqual({"Label A", "Label B"}, reader.class_labels)

    def test_ignored_ids(self):
        reader = cohort.CohortReader(config.ProjectConfig(f"{self.DATA_DIR}/ignore"))

        # Confirm 3, 4, and 5 got ignored
        self.assertEqual(
            {
                "adam": {1, 2},
                "allison": {1, 2},
            },
            reader.note_range,
        )

    def test_non_existent_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json", {"annotators": {"bob": 1}, "ranges": {"bob": ["1-5"]}}
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {"id": 1, "annotations": [{"completed_by": 1}]},  # done by bob
                    {"id": 3},  # not done by bob, but we are explicitly told it was
                ],
            )
            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))

            self.assertEqual({"bob": {1, 3}}, reader.note_range)

    def test_unknown_annotators_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(f"{tmpdir}/config.json", {"annotators": {"bob": 1}})
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {"id": 1, "annotations": [{"completed_by": 1}, {"completed_by": 2}]},
                ],
            )
            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))
            self.assertEqual({"bob": {1}}, reader.note_range)

    def test_uncredited_annotations_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [{"value": {"labels": ["cat"]}}],
                            },
                            {
                                # No completed_by
                                "result": [{"value": {"labels": ["bear"]}}],
                            },
                        ],
                    },
                ],
            )
            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))
            self.assertEqual({"1": {1: {"cat"}}}, reader.annotations.mentions)

    def test_prediction_annotations_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [
                                    {"origin": "prediction", "value": {"labels": ["cat"]}},
                                    {"origin": "manual", "value": {"labels": ["bear"]}},
                                ],
                            },
                        ],
                    },
                ],
            )
            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))
            self.assertEqual({"1": {1: {"bear"}}}, reader.annotations.mentions)

    def test_default_annotator_config(self):
        """Should use a string version of the completed_by ID for the names"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {"id": 1, "annotations": [{"completed_by": 1}, {"completed_by": 2}]},
                ],
            )
            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))
            self.assertEqual({"1": {1}, "2": {1}}, reader.note_range)

    def test_implied_labels_get_expanded(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {
                    "annotators": {"bob": 1},
                    "implied-labels": {
                        "cat": ["animal", "cat"],
                        "animal": "alive",
                    },
                },
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "annotations": [
                            {"completed_by": 1, "result": [{"value": {"labels": ["cat"]}}]},
                        ],
                    }
                ],
            )
            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))
            self.assertEqual({"bob": {1: {"cat", "animal", "alive"}}}, reader.annotations.mentions)
