"""Match external document references & labels to Label Studio data"""

import csv
import os
import sys
from typing import Optional

from chart_review import defines


def _load_csv_labels(filename: str) -> dict[str, defines.LabelSet]:
    """
    Loads a csv and returns a list of labels per row.

    CSV format is two columns, where the first is note/encounter id and the second is a single
    label.

    Returns {row_id -> set of labels for that ID}
    """
    id_to_labels = {}

    with open(filename, newline="", encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)

        header = next(reader, None)  # should be [row_id, label]
        id_header = header[0].lower()
        if "doc" in id_header or "note" in id_header:
            default_resource = "DocumentReference"
        elif "enc" in id_header:
            default_resource = "Encounter"
        else:
            print(
                f"Unrecognized ID column '{header[0]}'. Will assume Encounter ID.", file=sys.stderr
            )
            default_resource = "Encounter"

        for row in reader:
            row_id = row[0]
            if "/" not in row_id:
                row_id = f"{default_resource}/{row_id}"
            label_set = id_to_labels.setdefault(row_id, defines.LabelSet())
            if row[1]:  # allow for no labels for a row (no positive labels found)
                label_set.add(row[1])

    return id_to_labels


def _note_ref_to_label_studio_id(exported_json: list[dict], note_ref: str) -> Optional[int]:
    """Looks at the metadata in LS and grabs the note ID that holds the provided note ref"""
    for row in exported_json:
        mappings = row.get("data", {}).get("docref_mappings", {})
        for key, value in mappings.items():
            # Support older exports that didn't specify DocRef vs DxReport
            key = key if "/" in key else f"DocumentReference/{key}"
            value = value if "/" in value else f"DocumentReference/{value}"
            # Allow either an anonymous ID or the real ID -- collisions seem very unlikely
            # (i.e. real IDs aren't going to be formatted like our long anonymous ID hash)
            if key == note_ref or value == note_ref:
                return int(row["id"])
    return None


def _encounter_id_to_label_studio_id(exported_json: list[dict], enc_id: str) -> Optional[int]:
    """Looks at the metadata in LS and grabs the note ID that holds the provided encounter"""
    for row in exported_json:
        row_data = row.get("data", {})
        row_enc_id = row_data.get("encounter_id") or row_data.get("enc_id")  # old name
        row_anon_id = row_data.get("anon_encounter_id") or row_data.get("anon_id")  # old name
        # Allow either an anonymous ID or the real ID -- collisions seem very unlikely
        # (i.e. real IDs aren't going to be formatted like our long anonymous ID hash)
        if row_enc_id == enc_id or row_anon_id == enc_id:
            return int(row["id"])
    return None


def external_id_to_label_studio_id(
    exported_json: list[dict],
    row_id: str,
) -> Optional[int]:
    """Looks at the metadata in LS and grabs the note ID that holds the provided ID"""
    # First, check if there is a resource prefix, which will tell us which kind of ID this is
    parts = row_id.split("/", 1)
    if parts[0] == "Encounter" or len(parts) == 1:
        return _encounter_id_to_label_studio_id(exported_json, parts[-1])
    elif parts[0] in {"DiagnosticReport", "DocumentReference"}:
        return _note_ref_to_label_studio_id(exported_json, row_id)
    else:
        raise ValueError(f"Unrecognized resource type: {parts[0]}")  # pragma: no cover


def merge_external(
    annotations: defines.ProjectAnnotations,
    exported_json: list[dict],
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
    for row in exported_json:
        if "docref_mappings" not in row.get("data", {}):
            raise ValueError(
                "Your Label Studio export does not include note/encounter ID mapping metadata!\n"
                "Consider re-uploading your notes using Cumulus ETL's upload-notes command."
            )
        break  # just inspect one

    # Convert each row id into an LS id:
    external_mentions = annotations.mentions.setdefault(name, defines.Mentions())
    for row_id, label_set in label_map.items():
        ls_id = external_id_to_label_studio_id(exported_json, row_id)
        if ls_id is not None:
            all_labels = external_mentions.setdefault(ls_id, set())
            all_labels |= label_set
