"""Match external document references & labels to Label Studio data"""

import csv
import os
import sys

from chart_review import defines, studio


class ExternalCsvParser:
    def __init__(self, filename: str):
        self.filename = filename
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, newline="", encoding="utf8")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def __iter__(self):
        self._read_headers()
        return self

    def __next__(self) -> tuple[str, defines.Label | None]:
        row = next(self.reader)
        return self._row_to_id(row), self._row_to_label(row)

    def _read_headers(self):
        self.reader = csv.reader(self.file)

        # Remove case concerns
        header = next(self.reader, None)
        header = [x.casefold() for x in header]

        self.sublabel_name_col = None
        self.sublabel_value_col = None

        # There are two ways headers could be layed out:
        # - bare bones two column layout of id/label
        # - an ID column (with lots of possible names) and the standard label column names

        if len(header) == 2:
            # Implicit header order of [id, label]
            self.id_col = 0
            self.label_col = 1
            # The ID could be any of DocumentReference, DiagnosticReport, or Encounter.
            self.default_resource = self._check_col_name_for_res(header[0])
            if not self.default_resource:
                print(
                    f"Unrecognized ID column '{header[0]}'. Will assume Encounter ID.",
                    file=sys.stderr,
                )
                self.default_resource = "Encounter"
        else:
            # Search for ID column, assume label cols are using standard names
            for index, col_name in enumerate(header):
                self.default_resource = self._check_col_name_for_res(col_name)
                if self.default_resource:
                    self.id_col = index
                    break
            else:
                self._error("no resource ID column found")
            try:
                self.label_col = header.index("label")
            except ValueError:
                self._error("no 'label' column found")
            try:
                self.sublabel_name_col = header.index("sublabel_name")
            except ValueError:
                pass  # this is allowed
            if self.sublabel_name_col is not None:
                try:
                    self.sublabel_value_col = header.index("sublabel_value")
                except ValueError:
                    self._error("no 'sublabel_value' column found")

    def _row_to_id(self, row: list[str]) -> str:
        row_id = row[self.id_col]
        if "/" not in row_id:
            row_id = f"{self.default_resource}/{row_id}"
        return row_id

    def _row_to_label(self, row: list[str]) -> defines.Label | None:
        if not row[self.label_col]:  # allow for no labels for a row (no positive labels found)
            return None

        args = [row[self.label_col]]
        if self.sublabel_name_col is not None and self.sublabel_value_col is not None:
            args.append(row[self.sublabel_name_col])
            args.append(row[self.sublabel_value_col])

        return defines.Label(*args)

    def _check_col_name_for_res(self, col_name: str) -> str | None:
        if "doc" in col_name or col_name == "note_ref":
            return "DocumentReference"
        elif col_name in {"diagnosticreport_id", "diagnosticreport_ref"}:
            return "DiagnosticReport"
        elif "enc" in col_name:
            return "Encounter"
        else:
            return None

    def _error(self, msg: str):
        raise ValueError(f"Could not parse external file '{self.filename}': {msg}.")


def _load_csv_labels(filename: str) -> dict[str, defines.LabelSet]:
    """
    Loads a csv and returns a list of labels per row.

    CSV format is two columns, where the first is note/encounter id and the second is a single
    label.

    Returns {row_id -> set of labels for that ID}
    """
    id_to_labels = {}

    with ExternalCsvParser(filename) as parser:
        for row_id, label in parser:
            label_set = id_to_labels.setdefault(row_id, defines.LabelSet())
            if label:  # can be None if no labels given for a row
                label_set.add(label)

    return id_to_labels


def _note_ref_to_label_studio_id(export: studio.ExportFile, note_ref: str) -> int | None:
    """Looks at the metadata in LS and grabs the note ID that holds the provided note ref"""
    for note in export.notes:
        for key, value in note.docref_mappings.items():
            # Support older exports that didn't specify DocRef vs DxReport
            key = key if "/" in key else f"DocumentReference/{key}"
            value = value if "/" in value else f"DocumentReference/{value}"
            # Allow either an anonymous ID or the real ID -- collisions seem very unlikely
            # (i.e. real IDs aren't going to be formatted like our long anonymous ID hash)
            if key == note_ref or value == note_ref:
                return note.note_id
    return None


def _encounter_id_to_label_studio_id(export: studio.ExportFile, enc_id: str) -> int | None:
    """Looks at the metadata in LS and grabs the note ID that holds the provided encounter"""
    for note in export.notes:
        # Allow either an anonymous ID or the real ID -- collisions seem very unlikely
        # (i.e. real IDs aren't going to be formatted like our long anonymous ID hash)
        if note.encounter_id == enc_id or note.anon_encounter_id == enc_id:
            return note.note_id
    return None


def external_id_to_label_studio_id(
    export: studio.ExportFile,
    row_id: str,
) -> int | None:
    """Looks at the metadata in LS and grabs the note ID that holds the provided ID"""
    # First, check if there is a resource prefix, which will tell us which kind of ID this is
    parts = row_id.split("/", 1)
    if parts[0] == "Encounter" or len(parts) == 1:
        return _encounter_id_to_label_studio_id(export, parts[-1])
    elif parts[0] in {"DiagnosticReport", "DocumentReference"}:
        return _note_ref_to_label_studio_id(export, row_id)
    else:
        raise ValueError(f"Unrecognized resource type: {parts[0]}")  # pragma: no cover


def merge_external(
    annotations: defines.ProjectAnnotations,
    export: studio.ExportFile,
    project_dir: str,
    name: str,
    config: dict,
) -> None:
    """Loads an external csv file annotator and merges them into an existing simple dict"""
    if isinstance(config, dict) and (filename := config.get("filename")):
        full_filename = os.path.join(project_dir, filename)
        label_map = _load_csv_labels(full_filename)
    else:
        raise ValueError(f"Did not understand config for external annotator '{name}'")

    # Inspect exported json to see if it has the metadata we'll need.
    for note in export.notes:
        if not note.docref_mappings:
            raise ValueError(
                "Your Label Studio export does not include note/encounter ID mapping metadata!\n"
                "Consider re-uploading your notes using Cumulus ETL's upload-notes command."
            )
        break  # just inspect one

    # Convert each row id into an LS id:
    external_mentions = annotations.mentions.setdefault(name, defines.Mentions())
    for row_id, label_set in label_map.items():
        ls_id = external_id_to_label_studio_id(export, row_id)
        if ls_id is not None:
            all_labels = external_mentions.setdefault(ls_id, set())
            all_labels |= label_set
