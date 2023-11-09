"""Tests for external.py"""

import os
import shutil
import tempfile
import unittest

from chart_review import cohort

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestExternal(unittest.TestCase):
    """Test case for basic external ID merging"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_basic_read(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copytree(f"{DATA_DIR}/external", tmpdir, dirs_exist_ok=True)
            reader = cohort.CohortReader(tmpdir)

            self.assertEqual(
                {
                    "files": {1: 1, 2: 2},
                    "annotations": {
                        1: {
                            "human": [
                                {"labels": ["happy"], "text": "woo"},
                                {"labels": ["sad"], "text": "sigh"},
                            ],
                            # icd10 labels are split into two lists,
                            # because we used two different docrefs (anon & real)
                            "icd10": [{"labels": ["happy", "tired"]}, {"labels": ["hungry"]}],
                        },
                        # This was a note that didn't appear in the icd10 external annotations
                        # (and also didn't have a positive label by the human reviewer).
                        # Just here to test that it didn't screw anything up.
                        2: {
                            "human": [],
                        },
                    },
                },
                reader.annotations,
            )

            # Confirm ranges got auto-detected for both human and icd10
            self.assertEqual(
                {
                    "human": [1, 2],
                    "icd10": [1],
                },
                reader.note_range,
            )
