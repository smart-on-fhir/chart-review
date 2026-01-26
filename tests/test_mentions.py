"""Tests for commands/mentions.py"""

import tempfile

from chart_review import common
from tests import base


class TestMentions(base.TestCase):
    """Test case for the top-level mentions code"""

    def test_basic_output(self):
        stdout = self.run_cli("mentions", path=f"{self.DATA_DIR}/cold")

        self.assertEqual(
            """╭───────────┬──────────┬─────────┬──────────╮
│ Annotator │ Chart ID │ Mention │ Label    │
├───────────┼──────────┼─────────┼──────────┤
│ jane      │ 1        │ achoo   │ Cough    │
│ jane      │ 1        │ sigh    │ Fatigue  │
│ jane      │ 1        │ sigh    │ Headache │
│ jane      │ 4        │ pain    │ Headache │
│ jane      │ 4        │ sigh    │ Fatigue  │
│ jane      │ 4        │ sleepy  │ Fatigue  │
├───────────┼──────────┼─────────┼──────────┤
│ jill      │ 1        │ achoo   │ Cough    │
│ jill      │ 1        │ sigh    │ Fatigue  │
│ jill      │ 2        │ ouch    │ Fatigue  │
│ jill      │ 4        │ pain    │ Cough    │
│ jill      │ 4        │ sleepy  │ Fatigue  │
├───────────┼──────────┼─────────┼──────────┤
│ john      │ 1        │ achoo   │ Cough    │
│ john      │ 1        │ sigh    │ Fatigue  │
│ john      │ 2        │ ouch    │ Headache │
│ john      │ 4        │ pain    │ Headache │
│ john      │ 4        │ sleepy  │ Fatigue  │
╰───────────┴──────────┴─────────┴──────────╯
""",
            stdout,
        )

    def test_ignored(self):
        """Verify that we show info on ignored notes"""
        stdout = self.run_cli("mentions", path=f"{self.DATA_DIR}/ignore")

        # Blank mentions are correct - the ignore project doesn't list the source text.
        # Good to confirm that we still do something reasonable in this edge case.
        self.assertEqual(
            """╭───────────┬──────────┬─────────┬───────╮
│ Annotator │ Chart ID │ Mention │ Label │
├───────────┼──────────┼─────────┼───────┤
│ adam      │ 1        │         │ A     │
│ adam      │ 2        │         │ B     │
├───────────┼──────────┼─────────┼───────┤
│ allison   │ 1        │         │ A     │
│ allison   │ 2        │         │ B     │
╰───────────┴──────────┴─────────┴───────╯
  Ignoring 3 charts (3–5)
""",
            stdout,
        )

    def test_external(self):
        """Verify that we don't show external annotators"""
        stdout = self.run_cli("mentions", path=f"{self.DATA_DIR}/external")

        self.assertEqual(
            """╭───────────┬──────────┬─────────┬───────╮
│ Annotator │ Chart ID │ Mention │ Label │
├───────────┼──────────┼─────────┼───────┤
│ human     │ 1        │ sigh    │ sad   │
│ human     │ 1        │ woo     │ happy │
╰───────────┴──────────┴─────────┴───────╯
""",
            stdout,
        )

    def test_odd_text(self):
        """Verify that unusual text like multi-word unicode doesn't trip us up"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(f"{tmpdir}/config.json", {"annotators": {"chris": 1}})
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [
                                    {"value": {"text": "Cute Li🦁n", "labels": ["Cat"]}},
                                    {"value": {"text": "Multi\nLine-on", "labels": ["Cat"]}},
                                ],
                            },
                        ],
                    },
                ],
            )
            stdout = self.run_cli("mentions", path=tmpdir)

            self.assertEqual(
                """╭───────────┬──────────┬────────────┬───────╮
│ Annotator │ Chart ID │ Mention    │ Label │
├───────────┼──────────┼────────────┼───────┤
│ chris     │ 1        │ cute li🦁n │ Cat   │
│ chris     │ 1        │ multi      │ Cat   │
│           │          │ line-on    │       │
╰───────────┴──────────┴────────────┴───────╯
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
            stdout = self.run_cli("mentions", path=tmpdir)

            self.assertEqual(
                """╭───────────┬──────────┬─────────┬───────╮
│ Annotator │ Chart ID │ Mention │ Label │
├───────────┼──────────┼─────────┼───────┤
│ chris     │ 1        │ good    │ Valid │
╰───────────┴──────────┴─────────┴───────╯
""",
                stdout,
            )

    def test_duplicate_mention(self):
        """Verify that we don't show two copies of the same information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {
                    "annotators": {"chris": 1},
                    "labels": ["LabelA", "LabelB"],
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
                                    {"value": {"text": "dup", "labels": ["LabelA"]}},
                                    {"value": {"text": "dup", "labels": ["LabelA"]}},
                                    {"value": {"text": "new", "labels": ["LabelA"]}},
                                    {"value": {"text": "new", "labels": ["LabelB"]}},
                                ],
                            },
                        ],
                    },
                ],
            )
            stdout = self.run_cli("mentions", path=tmpdir)

            self.assertEqual(
                """╭───────────┬──────────┬─────────┬────────╮
│ Annotator │ Chart ID │ Mention │ Label  │
├───────────┼──────────┼─────────┼────────┤
│ chris     │ 1        │ dup     │ LabelA │
│ chris     │ 1        │ new     │ LabelA │
│ chris     │ 1        │ new     │ LabelB │
╰───────────┴──────────┴─────────┴────────╯
""",
                stdout,
            )

    def test_csv(self):
        """Verify that can print in CSV format"""
        stdout = self.run_cli("mentions", "--csv", path=f"{self.DATA_DIR}/external")

        self.assertEqual(
            [
                "annotator,chart_id,mention,label",
                "human,1,sigh,sad",
                "human,1,woo,happy",
            ],
            stdout.splitlines(),
        )

    def test_sublabels(self):
        output = self.run_cli("mentions", path=f"{self.DATA_DIR}/sublabels")
        self.assertEqual(
            output,
            """╭───────────┬──────────┬───────────────────────┬───────────────────────────────╮
│ Annotator │ Chart ID │ Mention               │ Label                         │
├───────────┼──────────┼───────────────────────┼───────────────────────────────┤
│ alice     │ 1308     │ alive                 │ Deceased → False              │
│ alice     │ 1308     │ alive                 │ Deceased → Datetime →         │
│           │          │                       │ 11/12/25                      │
│ alice     │ 1308     │ fungus found in lungs │ Fungal → Confirmed            │
│ alice     │ 1308     │ maybe got infected    │ Infection → Suspected         │
├───────────┼──────────┼───────────────────────┼───────────────────────────────┤
│ bob       │ 1308     │ alive                 │ Deceased → False              │
│ bob       │ 1308     │ alive                 │ Deceased → Datetime →         │
│           │          │                       │ 11/13/25                      │
│ bob       │ 1308     │ fungus found in lungs │ Fungal → Confirmed            │
│ bob       │ 1308     │ maybe got infected    │ Infection → Suspected         │
├───────────┼──────────┼───────────────────────┼───────────────────────────────┤
│ carla     │ 1308     │ alive                 │ Deceased → False              │
│ carla     │ 1308     │ alive                 │ Deceased → Datetime →         │
│           │          │                       │ 11/12/25                      │
│ carla     │ 1308     │ fungus found in lungs │ Fungal → Confirmed            │
│ carla     │ 1308     │ maybe got infected    │ Infection → Confirmed         │
╰───────────┴──────────┴───────────────────────┴───────────────────────────────╯
  Ignoring 2 invalid mentions
""",
        )
