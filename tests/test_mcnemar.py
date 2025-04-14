"""Tests for commands/mcnemar.py"""

from tests import base


class TestMcNemar(base.TestCase):
    """Test case for the McNemar code"""

    def test_default_output(self):
        stdout = self.run_cli(
            "mcnemar", "alice", "bob", "carla", path=f"{self.DATA_DIR}/many-notes"
        )

        # This tests the mid-P cutoff for b+c<25 (label B) as well as a low-significance and
        # a high-significance label.
        self.assertEqual(
            """Comparing 50 charts (1–50)
Truth: alice
Annotators: bob, carla

McNemar  P-value   BC  OL  OR  BW  Label
12.375   4.35e-04  20  61  27  42  *    
6.5      0.011     10  20  6   14  A    
N/A      0.035     1   16  6   27  B    
2.025    0.155     9   25  15  1   C    
""",
            stdout,
        )

    def test_csv(self):
        stdout = self.run_cli(
            "mcnemar", "--csv", "alice", "bob", "carla", path=f"{self.DATA_DIR}/many-notes"
        )

        self.assertEqual(
            [
                "mcnemar,p-value,bc,ol,or,bw,label",
                "12.375,4.35e-04,20,61,27,42,*",
                "6.5,0.011,10,20,6,14,A",
                ",0.035,1,16,6,27,B",
                "2.025,0.155,9,25,15,1,C",
            ],
            stdout.splitlines(),
        )

    def test_bad_annotator(self):
        """Verify that we do something suitable for bad arguments"""
        with self.capture_stderr() as stderr:
            with self.assertRaises(SystemExit):
                self.run_cli("mcnemar", "nope2", "john", "jill", path=f"{self.DATA_DIR}/cold")
        self.assertEqual("Unrecognized annotator 'nope2'\n", stderr.getvalue())

    def test_same_annotators(self):
        """Verify that we do something suitable for bad arguments"""
        with self.capture_stderr() as stderr:
            with self.assertRaises(SystemExit):
                self.run_cli("mcnemar", "john", "jill", "jill", path=f"{self.DATA_DIR}/cold")
        self.assertEqual("Can’t compare the same annotator with themselves.\n", stderr.getvalue())
