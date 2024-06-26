"""Tests for commands/frequency.py"""

import tempfile

from chart_review import common
from tests import base


class TestFrequency(base.TestCase):
    """Test case for the top-level frequency code"""

    def test_basic_output(self):
        stdout = self.run_cli("frequency", path=f"{self.DATA_DIR}/cold")

        self.assertEqual(
            """╭───────────┬──────────┬─────────┬───────╮
│ Annotator │ Label    │ Mention │ Count │
├───────────┼──────────┼─────────┼───────┤
│ All       │ Cough    │ achoo   │ 3     │
│ All       │ Cough    │ pain*   │ 1     │
│ All       │ Fatigue  │ sigh*   │ 5     │
│ All       │ Fatigue  │ sleepy  │ 3     │
│ All       │ Fatigue  │ ouch*   │ 2     │
│ All       │ Headache │ pain*   │ 2     │
│ All       │ Headache │ sigh*   │ 1     │
│ All       │ Headache │ ouch*   │ 1     │
├───────────┼──────────┼─────────┼───────┤
│ jane      │ Cough    │ achoo   │ 1     │
│ jane      │ Fatigue  │ sigh*   │ 2     │
│ jane      │ Fatigue  │ sleepy  │ 1     │
│ jane      │ Headache │ sigh*   │ 1     │
│ jane      │ Headache │ pain*   │ 1     │
├───────────┼──────────┼─────────┼───────┤
│ jill      │ Cough    │ pain*   │ 1     │
│ jill      │ Cough    │ achoo   │ 1     │
│ jill      │ Fatigue  │ ouch*   │ 2     │
│ jill      │ Fatigue  │ sleepy  │ 1     │
│ jill      │ Fatigue  │ sigh*   │ 1     │
├───────────┼──────────┼─────────┼───────┤
│ john      │ Cough    │ achoo   │ 1     │
│ john      │ Fatigue  │ sigh*   │ 2     │
│ john      │ Fatigue  │ sleepy  │ 1     │
│ john      │ Headache │ pain*   │ 1     │
│ john      │ Headache │ ouch*   │ 1     │
╰───────────┴──────────┴─────────┴───────╯
  * This text has multiple associated labels.
""",
            stdout,
        )

    def test_ignored(self):
        """Verify that we show info on ignored notes"""
        stdout = self.run_cli("frequency", path=f"{self.DATA_DIR}/ignore")

        # Showing empty mentions felt like the most reasonable approach to the edge case of
        # "no text in the annotation" - but also disabling the term confusion warning for
        # empty mentions.
        self.assertEqual(
            """╭───────────┬───────┬─────────┬───────╮
│ Annotator │ Label │ Mention │ Count │
├───────────┼───────┼─────────┼───────┤
│ All       │ A     │         │ 2     │
│ All       │ B     │         │ 2     │
├───────────┼───────┼─────────┼───────┤
│ adam      │ A     │         │ 1     │
│ adam      │ B     │         │ 1     │
├───────────┼───────┼─────────┼───────┤
│ allison   │ A     │         │ 1     │
│ allison   │ B     │         │ 1     │
╰───────────┴───────┴─────────┴───────╯
  Ignoring 3 charts (3–5)
""",
            stdout,
        )

    def test_external(self):
        """Verify that we don't show external annotators"""
        stdout = self.run_cli("frequency", path=f"{self.DATA_DIR}/external")

        self.assertEqual(
            """╭───────────┬───────┬─────────┬───────╮
│ Annotator │ Label │ Mention │ Count │
├───────────┼───────┼─────────┼───────┤
│ All       │ happy │ woo     │ 1     │
│ All       │ sad   │ sigh    │ 1     │
├───────────┼───────┼─────────┼───────┤
│ human     │ happy │ woo     │ 1     │
│ human     │ sad   │ sigh    │ 1     │
╰───────────┴───────┴─────────┴───────╯
""",
            stdout,
        )

    def test_unused_labels(self):
        """Verify that we don't list mentions for labels that aren't in consideration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {
                    "annotators": {"chris": 1},
                    "labels": ["Valid"],
                },
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [
                                    {"value": {"text": "good", "labels": ["Valid"]}},
                                    {"value": {"text": "bad", "labels": ["Invalid"]}},
                                ],
                            },
                        ],
                    },
                ],
            )
            stdout = self.run_cli("frequency", path=tmpdir)

            self.assertEqual(
                """╭───────────┬───────┬─────────┬───────╮
│ Annotator │ Label │ Mention │ Count │
├───────────┼───────┼─────────┼───────┤
│ All       │ Valid │ good    │ 1     │
├───────────┼───────┼─────────┼───────┤
│ chris     │ Valid │ good    │ 1     │
╰───────────┴───────┴─────────┴───────╯
""",
                stdout,
            )

    def test_spaces(self):
        """Verify that we handle text with surrounding spaces etc"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {
                    "annotators": {"chris": 1},
                    "labels": ["LabelA"],
                },
            )
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [
                                    {"value": {"text": "extra SPACES ", "labels": ["LabelA"]}},
                                    {"value": {"text": "\nextra spaces", "labels": ["LabelA"]}},
                                    {
                                        "value": {
                                            "text": "     Extra Spaces    ",
                                            "labels": ["LabelA"],
                                        }
                                    },
                                ],
                            },
                        ],
                    },
                ],
            )
            stdout = self.run_cli("frequency", path=tmpdir)

            self.assertEqual(
                """╭───────────┬────────┬──────────────┬───────╮
│ Annotator │ Label  │ Mention      │ Count │
├───────────┼────────┼──────────────┼───────┤
│ All       │ LabelA │ extra spaces │ 3     │
├───────────┼────────┼──────────────┼───────┤
│ chris     │ LabelA │ extra spaces │ 3     │
╰───────────┴────────┴──────────────┴───────╯
""",
                stdout,
            )

    def test_csv(self):
        """Verify that can print in CSV format"""
        stdout = self.run_cli("frequency", "--csv", path=f"{self.DATA_DIR}/external")

        self.assertEqual(
            [
                "annotator,label,mention,count",
                "All,happy,woo,1",
                "All,sad,sigh,1",
                "human,happy,woo,1",
                "human,sad,sigh,1",
            ],
            stdout.splitlines(),
        )
