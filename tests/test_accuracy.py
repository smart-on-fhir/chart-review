"""Tests for commands/accuracy.py"""

import shutil
import tempfile

from chart_review import common
from tests import base


class TestAccuracy(base.TestCase):
    """Test case for the top-level accuracy code"""

    def test_default_output(self):
        stdout = self.run_cli("accuracy", "jill", "jane", path=f"{self.DATA_DIR}/cold")

        self.assertEqual(
            """Comparing 3 charts (1, 3–4)
Truth: jill
Annotator: jane
Macro F1: 0.556

F1     Sens  Spec  PPV  NPV   Kappa  TP  FN  TN  FP  Label   
0.667  0.75  0.6   0.6  0.75  0.341  3   1   3   2   *       
0.667  0.5   1.0   1.0  0.5   0.4    1   1   1   0   Cough   
1.0    1.0   1.0   1.0  1.0   1.0    2   0   1   0   Fatigue 
0      0     0     0    0     0      0   0   1   2   Headache
""",
            stdout,
        )

    def test_csv(self):
        stdout = self.run_cli("accuracy", "--csv", "jill", "jane", path=f"{self.DATA_DIR}/cold")

        self.assertEqual(
            [
                "f1,sens,spec,ppv,npv,kappa,tp,fn,tn,fp,label",
                "0.667,0.75,0.6,0.6,0.75,0.341,3,1,3,2,*",
                "0.667,0.5,1.0,1.0,0.5,0.4,1,1,1,0,Cough",
                "1.0,1.0,1.0,1.0,1.0,1.0,2,0,1,0,Fatigue",
                "0,0,0,0,0,0,0,0,1,2,Headache",
            ],
            stdout.splitlines(),
        )

    def test_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copytree(f"{self.DATA_DIR}/cold", tmpdir, dirs_exist_ok=True)
            self.run_cli("accuracy", "--save", "jill", "jane", path=tmpdir)

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

    def test_save_and_csv_conflict(self):
        """Verify that --save and --csv can't run together"""
        with self.assertRaises(SystemExit) as cm:
            self.run_cli(
                "accuracy", "--save", "--csv", "jill", "jane", path=f"{self.DATA_DIR}/cold"
            )
        self.assertEqual(2, cm.exception.code)

    def test_verbose(self):
        output = self.run_cli("accuracy", "--verbose", "jill", "jane", path=f"{self.DATA_DIR}/cold")
        self.assertEqual(
            """Comparing 3 charts (1, 3–4)
Truth: jill
Annotator: jane

╭──────────┬──────────┬────────────────╮
│ Chart ID │ Label    │ Classification │
├──────────┼──────────┼────────────────┤
│ 1        │ Cough    │ TP             │
│ 1        │ Fatigue  │ TP             │
│ 1        │ Headache │ FP             │
├──────────┼──────────┼────────────────┤
│ 3        │ Cough    │ TN             │
│ 3        │ Fatigue  │ TN             │
│ 3        │ Headache │ TN             │
├──────────┼──────────┼────────────────┤
│ 4        │ Cough    │ FN             │
│ 4        │ Fatigue  │ TP             │
│ 4        │ Headache │ FP             │
╰──────────┴──────────┴────────────────╯
""",
            output,
        )

    def test_verbose_cvs(self):
        """Verify we can also print verbose results in CSV format"""
        stdout = self.run_cli(
            "accuracy", "--verbose", "--csv", "jill", "jane", path=f"{self.DATA_DIR}/cold"
        )
        self.assertEqual(
            [
                "chart_id,label,classification",
                "1,Cough,TP",
                "1,Fatigue,TP",
                "1,Headache,FP",
                "3,Cough,TN",
                "3,Fatigue,TN",
                "3,Headache,TN",
                "4,Cough,FN",
                "4,Fatigue,TP",
                "4,Headache,FP",
            ],
            stdout.splitlines(),
        )

    def test_bad_truth(self):
        """Verify that we do something suitable for bad arguments"""
        # Truth
        with self.capture_stderr() as stderr:
            with self.assertRaises(SystemExit):
                self.run_cli("accuracy", "nope1", "nope2", path=f"{self.DATA_DIR}/cold")
        self.assertEqual("Unrecognized annotator 'nope1'\n", stderr.getvalue())

        # Annotator
        with self.capture_stderr() as stderr:
            with self.assertRaises(SystemExit):
                self.run_cli("accuracy", "jill", "nope2", path=f"{self.DATA_DIR}/cold")
        self.assertEqual("Unrecognized annotator 'nope2'\n", stderr.getvalue())

    def test_same_annotators(self):
        """Verify that we do something suitable for bad arguments"""
        with self.capture_stderr() as stderr:
            with self.assertRaises(SystemExit):
                self.run_cli("accuracy", "jill", "jill", path=f"{self.DATA_DIR}/cold")
        self.assertEqual("Can’t compare the same annotator with themselves.\n", stderr.getvalue())
