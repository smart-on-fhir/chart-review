"""Tests for simplify.py"""

import ddt

from chart_review import defines, simplify
from tests import base


@ddt.ddt
class TestSimplify(base.TestCase):
    """Test case for annotation simplification"""

    @ddt.data(
        ({"Cat"}, {"Animal", "Cat", "Pet"}),  # Basic expansion
        ({"Animal", "Dangerous", "Venomous"}, {"Animal", "Risky"}),  # Basic grouping
        ({"Lion"}, {"Animal", "Cat", "Lion", "Pet", "Risky"}),  # Two layers deep, plus grouping
    )
    @ddt.unpack
    def test_simplify_mentions(self, input_labels, expected_labels):
        """Verify that we handle implied and grouped labels."""
        annotations = defines.ProjectAnnotations(
            # Note that the group names are not part of this label set yet.
            # This set generally starts with just the human-tagged input labels.
            labels={"Animal", "Cat", "Dangerous", "Lion", "Pet", "Venomous"},
            mentions={
                "katherine": {1: input_labels},
            },
        )
        simplify.simplify_mentions(
            annotations,
            implied_labels={
                "Cat": {"Animal", "Pet"},
                "Lion": {"Cat", "Dangerous"},
            },
            grouped_labels={
                # Dangerous overlaps with implied labels above, to test ordering
                "Risky": {"Dangerous", "Venomous"},
            },
        )
        self.assertEqual(expected_labels, annotations.mentions["katherine"][1])
        self.assertEqual({"Animal", "Cat", "Lion", "Pet", "Risky"}, annotations.labels)

    def test_binary_grouping(self):
        """Verify that grouping all labels down to a simple yes/no works as expected."""
        annotations = defines.ProjectAnnotations(
            labels={"Blue", "Green", "Red"},
            mentions={
                "paint-bot": {
                    1: {"Blue"},
                    2: set(),
                    3: {"Red", "Green"},
                },
            },
        )
        simplify.simplify_mentions(
            annotations,
            implied_labels={},
            grouped_labels={
                "Painted": {"Blue", "Green", "Red"},
            },
        )
        self.assertEqual(
            {1: {"Painted"}, 2: set(), 3: {"Painted"}},
            annotations.mentions["paint-bot"],
        )
        self.assertEqual({"Painted"}, annotations.labels)
