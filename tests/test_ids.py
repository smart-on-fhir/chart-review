"""Tests for commands/ids.py"""

import tempfile

from chart_review import common
from tests import base


class TestIDs(base.TestCase):
    """Test case for the top-level ids code"""

    def test_ids(self):
        """Verify that we pull IDs from all the places"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(
                f"{tmpdir}/config.json",
                {
                    "annotators": {"carl": 1},
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
                                    {
                                        "value": {
                                            "labels": [
                                                "My Label",
                                            ],
                                        },
                                    },
                                ],
                            },
                        ],
                        # only orig encounter, no docref mappings
                        "data": {
                            "enc_id": "Orig",
                        },
                    },
                    {
                        "id": 2,
                        # only anon encounter, a single docref mapping
                        "data": {
                            "anon_id": "Anon",
                            "docref_mappings": {
                                "Orig": "Anon",
                            },
                        },
                    },
                    {
                        "id": 3,
                        # no encounter info, multiple docref mappings
                        "data": {
                            "docref_mappings": {
                                "Orig1": "Anon1",
                                "Orig2": "Anon2",
                            },
                        },
                    },
                    {
                        "id": 4,
                        # full encounter info, no docref mappings
                        # (using modern, full field names)
                        "data": {
                            "encounter_id": "a",
                            "anon_encounter_id": "b",
                        },
                    },
                    {
                        "id": 5,
                        # no metadata at all
                    },
                ],
            )
            stdout = self.run_cli("ids", path=tmpdir)

        self.assertEqual(
            [
                "╭──────────┬─────────────────────────┬─────────────────────────╮",
                "│ Chart ID │ Original FHIR ID        │ Anonymized FHIR ID      │",
                "├──────────┼─────────────────────────┼─────────────────────────┤",
                "│ 1        │ Encounter/Orig          │                         │",
                "│ 2        │                         │ Encounter/Anon          │",
                "│ 2        │ DocumentReference/Orig  │ DocumentReference/Anon  │",
                "│ 3        │ DocumentReference/Orig1 │ DocumentReference/Anon1 │",
                "│ 3        │ DocumentReference/Orig2 │ DocumentReference/Anon2 │",
                "│ 4        │ Encounter/a             │ Encounter/b             │",
                "│ 5        │                         │                         │",
                "╰──────────┴─────────────────────────┴─────────────────────────╯",
            ],
            stdout.splitlines(),
        )

    def test_ids_csv(self):
        """Verify that we can print CSV output"""
        with tempfile.TemporaryDirectory() as tmpdir:
            common.write_json(f"{tmpdir}/config.json", {})
            common.write_json(
                f"{tmpdir}/labelstudio-export.json",
                [
                    {
                        "id": 1,
                        "data": {
                            # Verify that we quote correctly
                            "enc_id": "Orig,\\ 'Enc",
                            "anon_id": 'Anon "Enc',
                        },
                    },
                ],
            )
            stdout = self.run_cli("ids", "--csv", path=tmpdir)

        lines = stdout.splitlines()
        self.assertEqual(2, len(lines))
        self.assertEqual("chart_id,original_fhir_id,anonymized_fhir_id", lines[0])
        self.assertEqual('1,"Encounter/Orig,\\ \'Enc","Encounter/Anon ""Enc"', lines[1])
