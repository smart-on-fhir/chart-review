"""Tests for term_freq.py"""

import unittest

from chart_review import term_freq, types


class TestMentions(unittest.TestCase):
    """Test case for term frequency calculations"""

    def test_calc_term_freq(self):
        annotations = types.ProjectAnnotations(
            original_text_mentions={
                "hank": {
                    1: [
                        types.LabeledText("achoo", {"Cough", "Onomatopoeia"}),
                        types.LabeledText(None, {"Fever"}),
                        types.LabeledText("cough", {"Cough"}),
                    ]
                },
            },
        )
        self.assertEqual(
            {
                "ACHOO": {"Cough": [1], "Onomatopoeia": [1]},
                "COUGH": {"Cough": [1]},
            },
            term_freq.calc_term_freq(annotations, "hank"),
        )
