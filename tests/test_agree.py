"""Tests for agree.py"""

import unittest

import ddt

from chart_review import agree, types


@ddt.ddt
class TestAgreement(unittest.TestCase):
    """Test case for basic agreement logic"""

    @ddt.data(
        (
            "alice",
            "bob",
            None,
            {
                "FN": [{1: "Cough"}],
                "FP": [{1: "Headache"}, {2: "Cough"}],
                "TN": [{1: "Fever"}, {2: "Headache"}],
                "TP": [{2: "Fever"}],
            },
        ),
        (
            "bob",
            "alice",
            None,
            {
                "FN": [{1: "Headache"}, {2: "Cough"}],
                "FP": [{1: "Cough"}],
                "TN": [{1: "Fever"}, {2: "Headache"}],
                "TP": [{2: "Fever"}],
            },
        ),
        (
            "alice",
            "bob",
            ["Cough"],
            {
                "FN": [{1: "Cough"}],
                "FP": [{2: "Cough"}],
                "TN": [],
                "TP": [],
            },
        ),
    )
    @ddt.unpack
    def test_confusion_matrix_counts(self, truth, annotator, labels, expected_matrix):
        """Verify that we can make a simple confusion matrix."""
        annotations = types.ProjectAnnotations(
            labels={"Cough", "Fever", "Headache"},
            mentions={
                "alice": {1: {"Cough"}, 2: {"Fever"}},
                "bob": {1: {"Headache"}, 2: {"Cough", "Fever"}},
            },
        )
        notes = [1, 2]

        matrix = agree.confusion_matrix(annotations, truth, annotator, notes, labels=labels)
        self.assertEqual(expected_matrix, matrix)
