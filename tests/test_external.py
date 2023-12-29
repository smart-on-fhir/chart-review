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
                    "files": {1: 1, 2: 2, 3: 3},
                    "annotations": {
                        1: {
                            "human": [
                                {"labels": ["happy"], "text": "woo"},
                                {"labels": ["sad"], "text": "sigh"},
                            ],
                            # icd10 labels are split into two lists,
                            # because we used two different docrefs (anon & real)
                            "icd10-doc": [
                                {"labels": ["happy", "tired"]},
                                {"labels": ["sad"]},
                                {"labels": ["hungry"]},
                            ],
                            "icd10-enc": [
                                {"labels": ["happy", "tired"]},
                                {"labels": ["sad"]},
                                {"labels": ["hungry"]},
                            ],
                        },
                        # This was a note that didn't appear in the icd10 external annotations
                        # (and also didn't have a positive label by the human reviewer).
                        # Just here to test that it didn't screw anything up.
                        2: {
                            "human": [],
                        },
                        # This was an external annotation that said "saw it,
                        # but no labels for this note"
                        3: {
                            "human": [],
                            "icd10-doc": [],
                            "icd10-enc": [],
                        },
                    },
                },
                reader.annotations,
            )

            # Confirm ranges got auto-detected for both human and icd10
            self.assertEqual(
                {
                    "human": [1, 2, 3],
                    "icd10-doc": [1, 3],
                    "icd10-enc": [1, 3],
                },
                reader.note_range,
            )
