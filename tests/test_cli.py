"""Tests for cli.py"""

import os
import shutil
import tempfile
import unittest

from chart_review import cli, common

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestCommandLine(unittest.TestCase):
    """Test case for the top-level CLI code"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_accuracy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copytree(f"{DATA_DIR}/cold", tmpdir, dirs_exist_ok=True)
            cli.main_cli(["accuracy", "--project-dir", tmpdir, "jane", "john", "jill"])

            accuracy_json = common.read_json(f"{tmpdir}/accuracy-jane-john-jill.json")
            self.assertEqual(
                {
                    "Cough": {
                        "F1": 0.667,
                        "FN": 0,
                        "FP": 2,
                        "NPV": 1.0,
                        "PPV": 0.5,
                        "Sens": 1.0,
                        "Spec": 0.5,
                        "TN": 2,
                        "TP": 2,
                    },
                    "F1": 0.667,
                    "FN": 3,
                    "FP": 3,
                    "Fatigue": {
                        "F1": 0.889,
                        "FN": 0,
                        "FP": 1,
                        "NPV": 1.0,
                        "PPV": 0.8,
                        "Sens": 1.0,
                        "Spec": 0.5,
                        "TN": 1,
                        "TP": 4,
                    },
                    "Headache": {
                        "F1": 0,
                        "FN": 3,
                        "FP": 0,
                        "NPV": 0,
                        "PPV": 0,
                        "Sens": 0,
                        "Spec": 0,
                        "TN": 3,
                        "TP": 0,
                    },
                    "NPV": 0.667,
                    "PPV": 0.667,
                    "Sens": 0.667,
                    "Spec": 0.667,
                    "TN": 6,
                    "TP": 6,
                },
                accuracy_json,
            )

            accuracy_csv = common.read_text(f"{tmpdir}/accuracy-jane-john-jill.csv")
            self.assertEqual(
                """F1	Sens	Spec	PPV	NPV	TP	FN	TN	FP	Label
0.667	0.667	0.667	0.667	0.667	6	3	6	3	*
0.667	1.0	0.5	0.5	1.0	2	0	2	2	Cough
0.889	1.0	0.5	0.8	1.0	4	0	1	1	Fatigue
0	0	0	0	0	0	3	3	0	Headache
""",
                accuracy_csv,
            )
