"""Tests for agree.py"""

import ddt

from chart_review import agree, defines
from tests import base


@ddt.ddt
class TestAgreement(base.TestCase):
    """Test case for basic agreement logic"""

    @ddt.data(
        (
            "alice",
            "bob",
            None,
            {
                "FN": [{1: base.Label("Cough")}],
                "FP": [{1: base.Label("Headache")}, {2: base.Label("Cough")}],
                "TN": [{1: base.Label("Fever")}, {2: base.Label("Headache")}],
                "TP": [{2: base.Label("Fever")}],
            },
        ),
        (
            "bob",
            "alice",
            {},
            {
                "FN": [{1: base.Label("Headache")}, {2: base.Label("Cough")}],
                "FP": [{1: base.Label("Cough")}],
                "TN": [{1: base.Label("Fever")}, {2: base.Label("Headache")}],
                "TP": [{2: base.Label("Fever")}],
            },
        ),
        (
            "alice",
            "bob",
            base.labels(["Cough"]),
            {
                "FN": [{1: base.Label("Cough")}],
                "FP": [{2: base.Label("Cough")}],
                "TN": [],
                "TP": [],
            },
        ),
    )
    @ddt.unpack
    def test_confusion_matrix_counts(self, truth, annotator, labels, expected_matrix):
        """Verify that we can make a simple confusion matrix."""
        annotations = defines.ProjectAnnotations(
            labels={"Cough", "Fever", "Headache"},
            mentions={
                "alice": {1: base.labels({"Cough"}), 2: base.labels({"Fever"})},
                "bob": {1: base.labels({"Headache"}), 2: base.labels({"Cough", "Fever"})},
            },
        )
        notes = [1, 2]

        matrix = agree.confusion_matrix(annotations, truth, annotator, notes, labels=labels)
        self.assertEqual(expected_matrix, matrix)

    @ddt.data(
        # Examples pulled from https://en.wikipedia.org/wiki/Cohen's_kappa#Examples
        (
            {
                "FN": [{x: "Label"} for x in range(5)],
                "FP": [{x: "Label"} for x in range(10)],
                "TN": [{x: "Label"} for x in range(15)],
                "TP": [{x: "Label"} for x in range(20)],
            },
            0.4,
        ),
        (
            {
                "FN": [{x: "Label"} for x in range(15)],
                "FP": [{x: "Label"} for x in range(25)],
                "TN": [{x: "Label"} for x in range(15)],
                "TP": [{x: "Label"} for x in range(45)],
            },
            0.1304,
        ),
        (
            {
                "FN": [{x: "Label"} for x in range(35)],
                "FP": [{x: "Label"} for x in range(5)],
                "TN": [{x: "Label"} for x in range(35)],
                "TP": [{x: "Label"} for x in range(25)],
            },
            0.2593,
        ),
        # This example is from table 2 in https://pubmed.ncbi.nlm.nih.gov/12474424/
        (
            {
                "FN": [{x: "Label"} for x in range(6)],
                "FP": [{x: "Label"} for x in range(9)],
                "TN": [{x: "Label"} for x in range(26)],
                "TP": [{x: "Label"} for x in range(15)],
            },
            0.4444,
        ),
    )
    @ddt.unpack
    def test_kappa_score(self, matrix, expected_kappa):
        """Verify that we can score a matrix for kappa."""
        kappa = round(agree.score_kappa(matrix), 4)
        self.assertEqual(expected_kappa, kappa)
