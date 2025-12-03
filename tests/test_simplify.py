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
            labels=base.labels({"Animal", "Cat", "Dangerous", "Lion", "Pet", "Venomous"}),
            mentions={
                "katherine": {1: base.labels(input_labels)},
            },
        )
        simplify.simplify_mentions(
            annotations,
            implied_labels={
                base.LabelMatcher("Cat"): base.labels({"Animal", "Pet"}),
                base.LabelMatcher("Lion"): base.labels({"Cat", "Dangerous"}),
            },
            grouped_labels={
                # Dangerous overlaps with implied labels above, to test ordering
                base.Label("Risky"): base.LabelMatcher("Dangerous", "Venomous"),
            },
        )
        self.assertEqual(base.labels(expected_labels), annotations.mentions["katherine"][1])
        self.assertEqual(base.labels({"Animal", "Cat", "Lion", "Pet", "Risky"}), annotations.labels)

    def test_binary_grouping(self):
        """Verify that grouping all labels down to a simple yes/no works as expected."""
        annotations = defines.ProjectAnnotations(
            labels=base.labels({"Blue", "Green", "Red"}),
            mentions={
                "paint-bot": {
                    1: base.labels({"Blue"}),
                    2: set(),
                    3: base.labels({"Red", "Green"}),
                },
            },
        )
        simplify.simplify_mentions(
            annotations,
            implied_labels={},
            grouped_labels={base.Label("Painted"): base.LabelMatcher("Blue", "Green", "Red")},
        )
        self.assertEqual(
            {1: base.labels({"Painted"}), 2: set(), 3: base.labels({"Painted"})},
            annotations.mentions["paint-bot"],
        )
        self.assertEqual(base.labels({"Painted"}), annotations.labels)

    @ddt.data(
        (["A|B|C"], ["A|B|C"], True),
        (["A|B|D"], ["A|B|C"], False),
        (["A|B|C"], ["A|B"], True),
        (["A|C|D"], ["A|B"], False),
        (["A|B|C"], ["A"], True),
        (["B|C|D"], ["A"], False),
    )
    @ddt.unpack
    def test_sublabel_implied_matching(self, labels, config, add_to_expected):
        labels = base.labels(labels)
        annotations = defines.ProjectAnnotations(labels=labels, mentions={"alice": {1: labels}})
        simplify.simplify_mentions(
            annotations,
            implied_labels={base.LabelMatcher(*config): base.labels({"Implied"})},
            grouped_labels={},
        )
        if add_to_expected:
            labels.add(base.Label("Implied"))
        self.assertEqual(annotations.mentions["alice"][1], labels)
        self.assertEqual(annotations.labels, labels)

    @ddt.data(
        (["A"], ["Group", "H"]),
        (["A|B"], ["Group", "H", "A|M|N"]),
        (["A|B|C"], ["Group", "H", "A|B|D", "A|M|N"]),
    )
    @ddt.unpack
    def test_sublabel_group_matching(self, config, expected):
        all_labels = base.labels({"A|B|C", "A|B|D", "A|M|N", "H"})
        annotations = defines.ProjectAnnotations(
            labels=all_labels,
            mentions={"alice": {1: all_labels}},
        )
        simplify.simplify_mentions(
            annotations,
            implied_labels={},
            grouped_labels={base.Label("Group"): base.LabelMatcher(*config)},
        )
        self.assertEqual(annotations.mentions["alice"][1], base.labels(expected))
        self.assertEqual(annotations.labels, base.labels(expected))
