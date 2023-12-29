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

        matrix = agree.confusion_matrix(simple, truth, annotator, notes, labels=labels)
        self.assertEqual(expected_matrix, matrix)

    @ddt.data(
        # Truth labels, Annotator labels, all expected assignments
        (
            ["Animal"],
            ["Cat"],
            {"TP": [{1: "Animal"}], "FP": [{1: "Cat"}, {1: "Pet"}]},
        ),  # generic truth
        (
            ["Cat"],
            ["Animal"],
            {"TP": [{1: "Animal"}], "FN": [{1: "Cat"}, {1: "Pet"}]},
        ),  # specific truth
        (["Cat"], ["Cat"], {"TP": [{1: "Animal"}, {1: "Cat"}, {1: "Pet"}]}),  # specific agreement
        (["Animal"], ["Animal"], {"TP": [{1: "Animal"}]}),  # generic agreement
        # two layers deep, generic truth
        (
            ["Animal"],
            ["Lion"],
            {"TP": [{1: "Animal"}], "FP": [{1: "Cat"}, {1: "Lion"}, {1: "Pet"}]},
        ),
        # two layers deep, specific truth
        (
            ["Lion"],
            ["Animal"],
            {"TP": [{1: "Animal"}], "FN": [{1: "Cat"}, {1: "Lion"}, {1: "Pet"}]},
        ),
        # two layers deep, with mention of intermediate
        (
            ["Lion"],
            ["Animal", "Cat"],
            {"TP": [{1: "Animal"}, {1: "Cat"}, {1: "Pet"}], "FN": [{1: "Lion"}]},
        ),
    )
    @ddt.unpack
    def test_implied_labels(self, truth_labels, annotator_labels, expected_matrix):
        """Verify that we handle labels that imply other labels."""
        simple = {
            "annotations": {
                1: {
                    "truth": [{"labels": truth_labels}],
                    "annotator": [{"labels": annotator_labels}],
                },
            },
        }
        matrix = agree.confusion_matrix(
            simple,
            "truth",
            "annotator",
            [1],
            labels={"Animal", "Cat", "Lion", "Pet"},
            implied_labels={
                "Cat": {"Animal", "Pet"},
                "Lion": {"Cat"},
            },
        )
        full_expected_matrix = {"TP": [], "FP": [], "TN": [], "FN": []}
        full_expected_matrix.update(expected_matrix)
        self.assertEqual(full_expected_matrix, matrix)
