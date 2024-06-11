"""Tests for external.py"""

from chart_review import cohort, config
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
