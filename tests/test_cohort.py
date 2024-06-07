"""Tests for cohort.py"""

import os
import tempfile
import unittest

from chart_review import cohort, common, config

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestCohort(unittest.TestCase):
    """Test case for basic cohort management"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

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
        reader = cohort.CohortReader(config.ProjectConfig(f"{DATA_DIR}/ignore"))

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
