"""Tests for commands/accuracy.py"""

from tests import base


class TestAccuracy(base.TestCase):
    """Test case for the top-level accuracy code"""

    def test_default_output(self):
        stdout = self.run_cli("accuracy", "jill", "jane", path=f"{self.DATA_DIR}/cold")

        self.assertEqual(
            """Comparing 3 charts (1, 3–4)
Truth: jill
Annotator: jane
Macro F1: 0.833

F1     Sens  Spec   PPV  NPV   Kappa  TP  FN  TN  FP  Label   
0.667  0.75  0.6    0.6  0.75  0.341  3   1   3   2   *       
0.667  0.5   1.0    1.0  0.5   0.4    1   1   1   0   Cough   
1.0    1.0   1.0    1.0  1.0   1.0    2   0   1   0   Fatigue 
-      -     0.333  0.0  1.0   0.0    0   0   1   2   Headache
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
                ",,0.333,0.0,1.0,0.0,0,0,1,2,Headache",
            ],
            stdout.splitlines(),
        )

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

    def test_sublabels(self):
        output = self.run_cli("accuracy", "alice", "bob", path=f"{self.DATA_DIR}/sublabels")
        self.assertEqual(
            output,
            """Comparing 2 charts (1308–1309)
Truth: alice
Annotator: bob
Macro F1: 1.0

F1   Sens  Spec   PPV  NPV    Kappa   TP  FN  TN  FP  Label                     
0.6  0.6   0.778  0.6  0.778  0.378   3   2   7   2   *                         
-    0.0   1.0    -    0.5    0.0     0   1   1   0   Deceased                  
1.0  1.0   1.0    1.0  1.0    1.0     1   0   1   0   Deceased → *              
1.0  1.0   1.0    1.0  1.0    1.0     1   0   1   0   Deceased → False          
-    0.0   0.667  0.0  0.667  -0.333  0   1   2   1   Deceased → Datetime → *   
-    0.0   1.0    -    0.5    0.0     0   1   1   0   Deceased → Datetime →     
                                                      11/12/25                  
-    -     0.5    0.0  1.0    0.0     0   0   1   1   Deceased → Datetime →     
                                                      11/13/25                  
1.0  1.0   1.0    1.0  1.0    1.0     1   0   1   0   Fungal → *                
1.0  1.0   1.0    1.0  1.0    1.0     1   0   1   0   Fungal → Confirmed        
-    -     0.5    0.0  1.0    0.0     0   0   1   1   Infection                 
1.0  1.0   1.0    1.0  1.0    1.0     1   0   1   0   Infection → *             
-    -     -      -    -      -       0   0   0   0   Infection → Confirmed     
1.0  1.0   1.0    1.0  1.0    1.0     1   0   1   0   Infection → Suspected     
""",
        )
