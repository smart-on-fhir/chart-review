"""Tests for commands/accuracy.py"""

import os
import shutil
import tempfile
import unittest

from chart_review import cli, common

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestAccuracy(unittest.TestCase):
    """Test case for the top-level accuracy code"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_accuracy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copytree(f"{DATA_DIR}/cold", tmpdir, dirs_exist_ok=True)
            cli.main_cli(["accuracy", "--project-dir", tmpdir, "--save", "jill", "jane"])

            accuracy_json = common.read_json(f"{tmpdir}/accuracy-jill-jane.json")
            self.assertEqual(
                {
                    "F1": 0.667,
                    "Sens": 0.75,
                    "Spec": 0.6,
                    "PPV": 0.6,
                    "NPV": 0.75,
                    "Kappa": 0.341,
                    "TP": 3,
                    "FN": 1,
                    "TN": 3,
                    "FP": 2,
                    "Cough": {
                        "F1": 0.667,
                        "FN": 1,
                        "FP": 0,
                        "NPV": 0.5,
                        "PPV": 1.0,
                        "Sens": 0.5,
                        "Spec": 1.0,
                        "TN": 1,
                        "TP": 1,
                        "Kappa": 0.4,
                    },
                    "Fatigue": {
                        "F1": 1.0,
                        "FN": 0,
                        "FP": 0,
                        "NPV": 1.0,
                        "PPV": 1.0,
                        "Sens": 1.0,
                        "Spec": 1.0,
                        "TN": 1,
                        "TP": 2,
                        "Kappa": 1.0,
                    },
                    "Headache": {
                        "F1": 0,
                        "FN": 0,
                        "FP": 2,
                        "NPV": 0,
                        "PPV": 0,
                        "Sens": 0,
                        "Spec": 0,
                        "TN": 1,
                        "TP": 0,
                        "Kappa": 0,
                    },
                },
                accuracy_json,
            )

            accuracy_csv = common.read_text(f"{tmpdir}/accuracy-jill-jane.csv")
            self.assertEqual(
                """F1	Sens	Spec	PPV	NPV	Kappa	TP	FN	TN	FP	Label
0.667	0.75	0.6	0.6	0.75	0.341	3	1	3	2	*
0.667	0.5	1.0	1.0	0.5	0.4	1	1	1	0	Cough
1.0	1.0	1.0	1.0	1.0	1.0	2	0	1	0	Fatigue
0	0	0	0	0	0	0	0	1	2	Headache
""",
                accuracy_csv,
            )

    def test_custom_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(f"{DATA_DIR}/cold/labelstudio-export.json", tmpdir)
            cli.main_cli(
                [
                    "accuracy",
                    "--project-dir",
                    tmpdir,
                    "-c",
                    f"{DATA_DIR}/cold/config.yaml",
                    "jane",
                    "john",
                ]
            )  # just confirm it doesn't error out
