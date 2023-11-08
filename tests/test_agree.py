"""Tests for agree.py"""

import os
import tempfile
import unittest

import ddt

from chart_review import agree


@ddt.ddt
class TestAgreement(unittest.TestCase):
    """Test case for basic agreement logic"""

    @ddt.data(
        ("alice", "bob", None, {
            "FN": [{1: "Cough"}],
            "FP": [{1: "Headache"}, {2: "Cough"}],
            "TN": [{1: "Fever"}, {2: "Headache"}],
            "TP": [{2: "Fever"}],
        }),
        ("bob", "alice", None, {
            "FN": [{1: "Headache"}, {2: "Cough"}],
            "FP": [{1: "Cough"}],
            "TN": [{1: "Fever"}, {2: "Headache"}],
            "TP": [{2: "Fever"}],
        }),
        ("alice", "bob", "Cough", {
            "FN": [{1: "Cough"}],
            "FP": [{2: "Cough"}],
            "TN": [],
            "TP": [],
        }),
    )
    @ddt.unpack
    def test_confusion_matrix_counts(self, truth, annotator, label_pick, expected_matrix):
        """Verify that we can make a simple confusion matrix."""
        simple = {
            "annotations": {
                1: {
                    "alice": [{"labels": ["Cough"]}],
                    "bob": [{"labels": ["Headache"]}],
                },
                2: {
                    "alice": [{"labels": ["Fever"]}],
                    "bob": [{"labels": ["Fever", "Cough"]}],
                },
            },
        }
        notes = [1, 2]

        matrix = agree.confusion_matrix(simple, truth, annotator, notes, label_pick=label_pick)
        self.assertEqual(expected_matrix, matrix)
