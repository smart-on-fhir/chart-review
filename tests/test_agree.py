"""Tests for agree.py"""

import math

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
                "FN": [(1, "Cough", "")],
                "FP": [(1, "Headache", ""), (2, "Cough", "")],
                "TN": [(1, "Fever", ""), (2, "Headache", "")],
                "TP": [(2, "Fever", "")],
            },
        ),
        (
            "bob",
            "alice",
            {},
            {
                "FN": [(1, "Headache", ""), (2, "Cough", "")],
                "FP": [(1, "Cough", "")],
                "TN": [(1, "Fever", ""), (2, "Headache", "")],
                "TP": [(2, "Fever", "")],
            },
        ),
        (
            "alice",
            "bob",
            base.labels(["Cough"]),
            {
                "FN": [(1, "Cough", "")],
                "FP": [(2, "Cough", "")],
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

    def test_confusion_matrix_for_sublabels(self):
        annotations = defines.ProjectAnnotations(
            labels=base.labels({"Top|Sub|A", "Top|Sub|B", "Top|Sub|C"}),
            mentions={
                "alice": {
                    1: base.labels({"Top|Sub|A"}),  # TP
                    2: base.labels({"Top|Sub|A"}),  # FP
                    3: base.labels({"Top|Sub|A", "Top|Sub|B"}),  # TP
                    4: base.labels({"Top|Sub|A", "Top|Sub|B"}),  # FP
                    5: set(),  # TN
                    6: base.labels({"Top|Sub|A"}),  # FN
                    7: set(),  # FP
                },
                "bob": {
                    1: base.labels({"Top|Sub|A"}),  # TP
                    2: base.labels({"Top|Sub|C"}),  # FP
                    3: base.labels({"Top|Sub|A", "Top|Sub|B"}),  # TP
                    4: base.labels({"Top|Sub|C", "Top|Sub|B"}),  # FP
                    5: set(),  # TN
                    6: set(),  # FN
                    7: base.labels({"Top|Sub|A"}),  # FP
                },
            },
        )
        notes = [1, 2, 3, 4, 5, 6, 7]

        matrix = agree.confusion_matrix(annotations, "alice", "bob", notes)
        self.assertEqual(
            matrix,
            {
                "FN": [(6, "Top", "Sub")],
                "FP": [(2, "Top", "Sub"), (4, "Top", "Sub"), (7, "Top", "Sub")],
                "TN": [(5, "Top", "Sub")],
                "TP": [(1, "Top", "Sub"), (3, "Top", "Sub")],
            },
        )

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

    @ddt.data(
        # Example of incredibly unbalanced data, as a regression test
        (
            {
                "FN": [],
                "FP": [],
                "TN": [{x: "Label"} for x in range(90)],
                "TP": [],
            },
        ),
        (
            {
                "FN": [],
                "FP": [],
                "TN": [],
                "TP": [{x: "Label"} for x in range(90)],
            },
        ),
    )
    @ddt.unpack
    def test_unbalanced_kappa(self, matrix):
        """Verify that kappa will handle unbalanced NaN cases."""
        kappa = round(agree.score_kappa(matrix), 4)
        self.assertEqual(math.isnan(kappa), True)
