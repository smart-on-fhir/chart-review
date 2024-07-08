"""Tests for config.py"""

import os
import tempfile

import ddt

from chart_review import common, config
from tests import base


@ddt.ddt
class TestProjectConfig(base.TestCase):
    """Test case for basic config parsing"""

    def make_config(self, conf_text: str, filename: str = "config.yaml") -> config.ProjectConfig:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        common.write_text(os.path.join(tmpdir.name, filename), conf_text)
        return config.ProjectConfig(tmpdir.name)

    @ddt.data(
        (
            "yaml",
            """
            labels:
                - cough
                - fever
            annotators:
                jane: 1
                john: 2
            ranges:
                jane: [3]
                john: [1, 3, 5]
        """,
        ),
        (
            "json",
            """
            {
                "labels": ["cough", "fever"],
                "annotators": {"jane": 1, "john": 2},
                "ranges": {"jane": [3], "john": [1, 3, 5]}
            }
        """,
        ),
    )
    @ddt.unpack
    def test_multiple_formats(self, suffix, text):
        """Verify that we can operate on multiple formats (like json & yaml)."""
        proj_config = self.make_config(text, filename=f"config.{suffix}")

        self.assertEqual({"cough", "fever"}, proj_config.class_labels)
        self.assertEqual({1: "jane", 2: "john"}, proj_config.annotators)
        self.assertEqual({"jane": [3], "john": [1, 3, 5]}, proj_config.note_ranges)

    def test_range_syntax(self):
        """Verify that we support interesting note range syntax options."""
        with self.capture_stderr() as stderr:
            proj_config = self.make_config(
                """
                ranges:
                    bare_num: 1
                    string_num: "2"
                    range: 3-5
                    reference: bare_num
                    array: [1, "2", range]
                    invalid: [not_defined, 1]
            """
            )

        self.assertEqual(
            {
                "bare_num": [1],
                "string_num": [2],
                "range": [3, 4, 5],
                "reference": [1],
                "array": [1, 2, 3, 4, 5],
                "invalid": [1],
            },
            proj_config.note_ranges,
        )
        self.assertEqual(stderr.getvalue(), "Unknown note range 'not_defined'\n")

    def test_grouped_labels(self):
        """Verify that we grab the label config correctly."""
        proj_config = self.make_config(
            """
            grouped-labels:
                A: B
                C: [D, E]
            """
        )

        self.assertEqual(
            {
                "A": {"B"},
                "C": {"D", "E"},
            },
            proj_config.grouped_labels,
        )

    def test_implied_labels(self):
        """Verify that we grab the label config correctly."""
        proj_config = self.make_config(
            """
            implied-labels:
                A: B
                C: [D, E]
            """
        )

        self.assertEqual(
            {
                "A": {"B"},
                "C": {"D", "E"},
            },
            proj_config.implied_labels,
        )
