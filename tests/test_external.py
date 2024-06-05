"""Tests for external.py"""

import os
import shutil
import tempfile
import unittest

from chart_review import cohort, config

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestExternal(unittest.TestCase):
    """Test case for basic external ID merging"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_basic_read(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copytree(f"{DATA_DIR}/external", tmpdir, dirs_exist_ok=True)
            reader = cohort.CohortReader(config.ProjectConfig(tmpdir))

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
