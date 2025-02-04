"""Match external document references & labels to Label Studio data"""

import csv
import enum
import os
import sys
from typing import Optional

from chart_review import defines


class IdentifierType(enum.Enum):
    DOCREF = enum.auto()
    ENCOUNTER = enum.auto()


def _load_csv_labels(filename: str) -> tuple[IdentifierType, dict[str, defines.LabelSet]]:
    """
    Loads a csv and returns a list of labels per row.

    CSV format is two columns, where the first is docref/encounter id and the second is a single
    label.

    Returns id_type, {row_id -> set of labels for that ID}
    """
    id_to_labels = {}

    with open(filename, newline="", encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)

        header = next(reader, None)  # should be [row_id, label]
        id_header = header[0].lower()
        if "doc" in id_header:
            id_type = IdentifierType.DOCREF
        elif "enc" in id_header:
            id_type = IdentifierType.ENCOUNTER
        else:
            print(
                f"Unrecognized ID column '{header[0]}'. Will assume Encounter ID.", file=sys.stderr
            )
            id_type = IdentifierType.ENCOUNTER

        for row in reader:
            row_id = row[0]
            label_set = id_to_labels.setdefault(row_id, defines.LabelSet())
            if row[1]:  # allow for no labels for a row (no positive labels found)
                label_set.add(row[1])

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


def external_id_to_label_studio_id(
    exported_json: list[dict],
    row_id: str,
    default_id_type: IdentifierType = IdentifierType.ENCOUNTER,
) -> Optional[int]:
    """Looks at the metadata in LS and grabs the note ID that holds the provided ID"""
    # First, check if there is a resource prefix, which will tell us which kind of ID this is
    parts = row_id.split("/")
    if parts[0] == "Encounter":
        id_type = IdentifierType.ENCOUNTER
        row_id = parts[1]
    elif parts[0] == "DocumentReference":
        id_type = IdentifierType.DOCREF
        row_id = parts[1]
    else:
        # Who knows - let's just use the provided default
        id_type = default_id_type

    if id_type == IdentifierType.ENCOUNTER:
        return _encounter_id_to_label_studio_id(exported_json, row_id)
    else:
        return _docref_id_to_label_studio_id(exported_json, row_id)


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
        detected_id_type, label_map = _load_csv_labels(full_filename)
    else:
        raise ValueError(f"Did not understand config for external annotator '{name}'")

    # Inspect exported json to see if it has the metadata we'll need.
    for row in exported_json:
        if "docref_mappings" not in row.get("data", {}):
            raise ValueError(
                "Your Label Studio export does not include DocRef/Encounter ID mapping metadata!\n"
                "Consider re-uploading your notes using Cumulus ETL's chart-review command."
            )
        break  # just inspect one

    # Convert each row id into an LS id:
    external_mentions = annotations.mentions.setdefault(name, defines.Mentions())
    for row_id, label_set in label_map.items():
        ls_id = external_id_to_label_studio_id(
            exported_json,
            row_id,
            default_id_type=detected_id_type,
        )
        if ls_id is not None:
            all_labels = external_mentions.setdefault(ls_id, set())
            all_labels |= label_set
