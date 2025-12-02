"""Tests for studio.py"""

import json
import tempfile

from chart_review import studio
from tests import base


class TestStudio(base.TestCase):
    """Test some edge cases with Label Studio export parsing"""

    def test_invalid_label_type(self):
        with tempfile.NamedTemporaryFile("wt") as tmpfile:
            json.dump(
                [
                    {
                        "id": 1,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [
                                    {
                                        "value": {"labels": ["A"]},
                                        "type": "bogus",
                                    }
                                ],
                            },
                        ],
                    },
                ],
                tmpfile,
            )
            tmpfile.flush()
            with self.assertRaisesRegex(ValueError, "Unrecognized Label Studio result type"):
                studio.ExportFile(tmpfile.name)

    def test_invalid_label_id(self):
        with tempfile.NamedTemporaryFile("wt") as tmpfile:
            json.dump(
                [
                    {
                        "id": 1,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [
                                    {
                                        "id": "id1",
                                        "value": {"labels": ["A"]},
                                        "type": "labels",
                                        "from_name": "label",
                                    },
                                    {
                                        "id": "id1",
                                        "value": {"choices": ["A1.1"]},
                                        "type": "choices",
                                        "from_name": "A",
                                    },
                                    {
                                        "id": "bogus-id",
                                        "value": {"choices": ["A1.2"]},
                                        "type": "choices",
                                        "from_name": "A",
                                    },
                                ],
                            },
                        ],
                        "data": {"text": "", "label": []},
                    },
                ],
                tmpfile,
            )
            tmpfile.flush()
            with self.assertRaisesRegex(ValueError, "Unrecognized sublabel ID 'bogus-id'."):
                studio.ExportFile(tmpfile.name)
