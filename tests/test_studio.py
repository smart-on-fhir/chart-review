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

    def test_merging(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(f"{tmpdir}/one.json", "w", encoding="utf8") as f:
                json.dump(
                    [
                        {
                            "id": 1,
                            "annotations": [
                                {
                                    "completed_by": 1,
                                    "result": [{"value": {"labels": ["LabelA"]}}],
                                },
                                {
                                    "completed_by": 2,
                                    "result": [{"value": {"labels": ["LabelB"]}}],
                                },
                            ],
                            "data": {
                                "docref_mappings": {"A": "anonA", "B": "anonB"},
                            },
                        },
                    ],
                    f,
                )
            with open(f"{tmpdir}/two.json", "w", encoding="utf8") as f:
                json.dump(
                    [
                        {
                            "id": 2,
                            "annotations": [
                                {
                                    "completed_by": 1,
                                    "result": [{"value": {"labels": ["LabelC"]}}],
                                },
                                {
                                    "completed_by": 3,
                                    "result": [{"value": {"labels": ["LabelD"]}}],
                                },
                            ],
                            "data": {
                                "docref_mappings": {"A": "anonA", "B": "anonB"},
                            },
                        },
                    ],
                    f,
                )
            with open(f"{tmpdir}/three.json", "w", encoding="utf8") as f:
                json.dump(
                    [
                        {
                            "id": 3,
                            "annotations": [
                                {
                                    "completed_by": 1,
                                    "result": [{"value": {"labels": ["LabelE"]}}],
                                },
                            ],
                            "data": {
                                # Will not be merged, because this doesn't fully match other notes
                                "docref_mappings": {"A": "anonA"},
                            },
                        },
                    ],
                    f,
                )

            merged = studio.ExportFile(tmpdir)

        self.assertEqual(
            merged.notes,
            [
                studio.Note.parse(
                    {
                        "id": 1,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [
                                    {"value": {"labels": ["LabelA"]}},
                                    {"value": {"labels": ["LabelC"]}},
                                ],
                            },
                            {
                                "completed_by": 2,
                                "result": [{"value": {"labels": ["LabelB"]}}],
                            },
                            {
                                "completed_by": 3,
                                "result": [{"value": {"labels": ["LabelD"]}}],
                            },
                        ],
                        "data": {
                            "docref_mappings": {"A": "anonA", "B": "anonB"},
                        },
                    }
                ),
                studio.Note.parse(
                    {
                        "id": 3,
                        "annotations": [
                            {
                                "completed_by": 1,
                                "result": [{"value": {"labels": ["LabelE"]}}],
                            },
                        ],
                        "data": {
                            "docref_mappings": {"A": "anonA"},
                        },
                    }
                ),
            ],
        )

    def test_bad_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(f"{tmpdir}/invalid.json", "w", encoding="utf8") as f:
                f.write('[{"id": ]')
            with open(f"{tmpdir}/strings.json", "w", encoding="utf8") as f:
                f.write('["string list"]')
            with open(f"{tmpdir}/no-id.json", "w", encoding="utf8") as f:
                f.write('[{"random": "yup"}]')
            with open(f"{tmpdir}/valid.json", "w", encoding="utf8") as f:
                f.write('[{"id": 1}]')

            self.assertEqual(
                studio.ExportFile(tmpdir).notes,
                [studio.Note.parse({"id": 1})],
            )

    def test_supported_types(self):
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
                                        "value": {"choices": ["Choice"]},
                                        "type": "choices",
                                    },
                                    {
                                        "value": {"datetime": "2021-04-22"},
                                        "type": "datetime",
                                    },
                                    {
                                        "value": {"datetime": "2021-04-22T10:20:30Z"},
                                        "type": "datetime",
                                    },
                                    {
                                        "value": {"labels": ["Label"]},
                                        "type": "labels",
                                    },
                                    {
                                        "value": {"text": ["Text"]},
                                        "type": "textarea",
                                    },
                                ],
                            },
                        ],
                    },
                ],
                tmpfile,
            )
            tmpfile.flush()
            export = studio.ExportFile(tmpfile.name)

        self.assertEqual(
            [x.labels for x in export.notes[0].annotations[0].mentions],
            [
                base.labels(["Choice"]),
                base.labels(["2021-04-22"]),
                base.labels(["2021-04-22T10:20:30Z"]),
                base.labels(["Label"]),
                base.labels(["Text"]),
            ],
        )
