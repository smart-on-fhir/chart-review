"""Match external document references & labels to Label Studio data"""

import csv
import enum
import os
import sys
from typing import Optional

from chart_review import simplify


class IdentifierType(enum.Enum):
    DOCREF = enum.auto()
    ENCOUNTER = enum.auto()


def _load_csv_labels(filename: str) -> tuple[IdentifierType, dict[str, list[str]]]:
    """
    Loads a csv and returns a list of labels per row.

    CSV format is two columns, where the first is docref/encounter id and the second is a single
    label.

    Returns id_type, {row_id -> list of labels for that ID}
    """
    id_to_labels = {}

    with open(filename, "r", newline="", encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)

        header = next(reader, None)  # should be [row_id, label]
        id_header = header[0].lower()
        if "doc" in id_header:
            id_type = IdentifierType.DOCREF
        elif "enc" in id_header:
            id_type = IdentifierType.ENCOUNTER
        else:
            print(f"Unrecognized ID column '{header[0]}'. Will assume DocRef ID.", file=sys.stderr)
            id_type = IdentifierType.DOCREF

        for row in reader:
            docref_id = row[0]
            label_list = id_to_labels.setdefault(docref_id, [])
            if row[1]:  # allow for no labels for a row (no positive labels found)
                label_list.append(row[1])

    return id_type, id_to_labels


def _docref_id_to_label_studio_id(exported_json: list[dict], docref_id: str) -> Optional[int]:
    """Looks at the metadata in LS and grabs the note ID that holds the provided docref"""
    for row in exported_json:
        mappings = row.get("data", {}).get("docref_mappings", {})
        for key, value in mappings.items():
            # Allow either an anonymous ID or the real ID -- collisions seem very unlikely
            # (i.e. real IDs aren't going to be formatted like our long anonymous ID hash)
            if key == docref_id or value == docref_id:
                return int(row["id"])
    return None


def _encounter_id_to_label_studio_id(exported_json: list[dict], enc_id: str) -> Optional[int]:
    """Looks at the metadata in LS and grabs the note ID that holds the provided encounter"""
    for row in exported_json:
        row_data = row.get("data", {})
        row_enc_id = row_data.get("enc_id")
        row_anon_id = row_data.get("anon_id")
        # Allow either an anonymous ID or the real ID -- collisions seem very unlikely
        # (i.e. real IDs aren't going to be formatted like our long anonymous ID hash)
        if row_enc_id == enc_id or row_anon_id == enc_id:
            return int(row["id"])
    return None


def _row_id_to_label_studio_id(
    exported_json: list[dict], id_type: IdentifierType, row_id: str
) -> Optional[int]:
    """Looks at the metadata in LS and grabs the note ID that holds the provided ID"""
    if id_type == IdentifierType.ENCOUNTER:
        return _encounter_id_to_label_studio_id(exported_json, row_id)
    else:
        return _docref_id_to_label_studio_id(exported_json, row_id)


def merge_external(
    simple: dict, exported_json: list[dict], project_dir: str, name: str, config: dict
) -> dict:
    """Loads an external csv file annotator and merges them into an existing simple dict"""
    if filename := config.get("filename"):
        full_filename = os.path.join(project_dir, filename)
        id_type, label_map = _load_csv_labels(full_filename)
    else:
        sys.exit(f"Did not understand config for external annotator '{name}'")

    # Inspect exported json to see if it has the metadata we'll need.
    for row in exported_json:
        if "docref_mappings" not in row.get("data", {}):
            sys.exit(
                f"Your Label Studio export does not include DocRef/Encounter ID mapping metadata!\n"
                f"Consider re-uploading your notes using Cumulus ETL's chart-review command."
            )
        break  # just inspect one

    # Convert each row id into an LS id:
    external_simple = {"files": {}, "annotations": {}}
    for row_id, label_list in label_map.items():
        ls_id = _row_id_to_label_studio_id(exported_json, id_type, row_id)
        if ls_id is None:
            continue

        external_simple["files"][ls_id] = ls_id
        annotation_list = external_simple["annotations"].setdefault(ls_id, {}).setdefault(name, [])
        annotation_list.append({"labels": label_list})

    # Merge into existing simple dictionary
    return simplify.merge_simple(simple, external_simple)
